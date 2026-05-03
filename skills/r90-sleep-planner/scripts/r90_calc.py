#!/usr/bin/env python3
"""Deterministic R90 sleep-window and weekly-cycle calculations."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.9+ has zoneinfo.
    ZoneInfo = None  # type: ignore[assignment]


TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


@dataclass(frozen=True)
class SleepPlanInput:
    wake_time: str
    wake_date: date
    cycle_options: tuple[int, ...] = (4, 5, 6)
    wind_down_minutes: int = 30
    timezone: str | None = None


def parse_hhmm(value: str) -> time:
    match = TIME_RE.match(value)
    if not match:
        raise ValueError("wakeTime must use HH:mm in 24-hour time")
    return time(hour=int(match.group(1)), minute=int(match.group(2)))


def parse_date(value: str | None) -> date:
    if not value:
        return date.today()
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("wakeDate/weekStart must use YYYY-MM-DD") from exc


def parse_cycles(value: str | None) -> tuple[int, ...]:
    if not value:
        return (4, 5, 6)
    cycles: list[int] = []
    for raw in value.split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            cycle = int(raw)
        except ValueError as exc:
            raise ValueError("cycles must be comma-separated integers") from exc
        if cycle < 1 or cycle > 7:
            raise ValueError("cycle counts must be between 1 and 7")
        cycles.append(cycle)
    if not cycles:
        raise ValueError("cycles must include at least one count")
    return tuple(cycles)


def load_tz(name: str | None):
    if not name:
        return datetime.now().astimezone().tzinfo
    if ZoneInfo is None:
        raise ValueError("IANA timezones require Python 3.9+ zoneinfo")
    try:
        return ZoneInfo(name)
    except Exception as exc:
        raise ValueError(f"unknown IANA timezone: {name}") from exc


def subtract_elapsed(local_dt: datetime, minutes: int) -> datetime:
    if local_dt.tzinfo is None:
        return local_dt - timedelta(minutes=minutes)
    return (local_dt.astimezone(UTC) - timedelta(minutes=minutes)).astimezone(local_dt.tzinfo)


def iso_local(dt: datetime) -> str:
    return dt.isoformat(timespec="minutes")


def calculate_windows(input_data: SleepPlanInput) -> list[dict[str, Any]]:
    if input_data.wind_down_minutes < 0 or input_data.wind_down_minutes > 120:
        raise ValueError("windDownMinutes must be between 0 and 120")

    wake_dt = datetime.combine(
        input_data.wake_date,
        parse_hhmm(input_data.wake_time),
        tzinfo=load_tz(input_data.timezone),
    )

    windows: list[dict[str, Any]] = []
    for cycle_count in sorted(set(input_data.cycle_options), reverse=True):
        sleep_minutes = cycle_count * 90
        lights_out = subtract_elapsed(wake_dt, sleep_minutes)
        in_bed = subtract_elapsed(lights_out, input_data.wind_down_minutes)
        notes: list[str] = []

        if lights_out.date() < wake_dt.date():
            notes.append("lights-out falls on the previous calendar day")
        if in_bed.date() < lights_out.date():
            notes.append("wind-down starts on the previous calendar day")
        if wake_dt.utcoffset() != lights_out.utcoffset():
            notes.append("timezone offset changes between lights-out and wake time")

        windows.append(
            {
                "cycleCount": cycle_count,
                "sleepMinutes": sleep_minutes,
                "sleepHours": round(sleep_minutes / 60, 2),
                "label": f"{cycle_count} cycles",
                "inBedAt": iso_local(in_bed),
                "lightsOutAt": iso_local(lights_out),
                "wakeAt": iso_local(wake_dt),
                "notes": notes,
            }
        )
    return windows


def summarize_week(
    entries: list[dict[str, Any]],
    week_start: date,
    target_cycles: int = 35,
    minimum_useful_range: tuple[int, int] = (28, 30),
) -> dict[str, Any]:
    week_end = week_start + timedelta(days=6)
    rows_by_date: dict[str, dict[str, Any]] = {}

    for entry in entries:
        entry_date_raw = entry.get("date")
        if not isinstance(entry_date_raw, str):
            raise ValueError("each entry requires date as YYYY-MM-DD")
        entry_date = parse_date(entry_date_raw)
        if week_start <= entry_date <= week_end:
            actual = int(entry.get("actualCycles", 0))
            planned_raw = entry.get("plannedCycles")
            if actual < 0 or actual > 7:
                raise ValueError("actualCycles must be between 0 and 7")
            if planned_raw is not None and (int(planned_raw) < 0 or int(planned_raw) > 7):
                raise ValueError("plannedCycles must be between 0 and 7")
            rows_by_date[entry_date.isoformat()] = {
                "date": entry_date.isoformat(),
                "actualCycles": actual,
                "plannedCycles": int(planned_raw) if planned_raw is not None else None,
                "note": entry.get("note"),
            }

    days: list[dict[str, Any]] = []
    for offset in range(7):
        current = week_start + timedelta(days=offset)
        key = current.isoformat()
        days.append(rows_by_date.get(key, {"date": key, "actualCycles": 0, "plannedCycles": None, "note": None}))

    actual_cycles = sum(int(day["actualCycles"]) for day in days)
    planned_cycles = sum(int(day["plannedCycles"]) for day in days if day["plannedCycles"] is not None)
    cycles_to_minimum = max(minimum_useful_range[0] - actual_cycles, 0)
    cycles_to_target = max(target_cycles - actual_cycles, 0)

    if actual_cycles >= target_cycles:
        status = "met_target"
    elif actual_cycles < minimum_useful_range[0]:
        status = "below_minimum"
    else:
        status = "below_target"

    return {
        "weekStart": week_start.isoformat(),
        "weekEnd": week_end.isoformat(),
        "actualCycles": actual_cycles,
        "plannedCycles": planned_cycles,
        "targetCycles": target_cycles,
        "cyclesToTarget": cycles_to_target,
        "minimumUsefulRange": list(minimum_useful_range),
        "cyclesToMinimum": cycles_to_minimum,
        "status": status,
        "days": days,
    }


def read_entries(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.entries_file:
        data = json.loads(Path(args.entries_file).read_text(encoding="utf-8"))
    elif args.entries_json:
        data = json.loads(args.entries_json)
    else:
        data = []
    if not isinstance(data, list):
        raise ValueError("entries must be a JSON array")
    return data


def cmd_windows(args: argparse.Namespace) -> dict[str, Any]:
    input_data = SleepPlanInput(
        wake_time=args.wake_time,
        wake_date=parse_date(args.wake_date),
        cycle_options=parse_cycles(args.cycles),
        wind_down_minutes=args.wind_down,
        timezone=args.timezone,
    )
    return {
        "input": {
            "wakeTime": input_data.wake_time,
            "wakeDate": input_data.wake_date.isoformat(),
            "cycleOptions": list(input_data.cycle_options),
            "windDownMinutes": input_data.wind_down_minutes,
            "timezone": input_data.timezone,
        },
        "windows": calculate_windows(input_data),
        "disclaimer": "R90 output is planning guidance, not medical advice.",
    }


def cmd_weekly(args: argparse.Namespace) -> dict[str, Any]:
    return summarize_week(
        entries=read_entries(args),
        week_start=parse_date(args.week_start),
        target_cycles=args.target,
    )


def cmd_self_test(_: argparse.Namespace) -> dict[str, Any]:
    windows = calculate_windows(
        SleepPlanInput(
            wake_time="07:00",
            wake_date=date(2026, 5, 4),
            cycle_options=(4, 5, 6),
            wind_down_minutes=30,
            timezone="Asia/Shanghai",
        )
    )
    by_cycle = {row["cycleCount"]: row for row in windows}
    assert by_cycle[6]["lightsOutAt"].startswith("2026-05-03T22:00")
    assert by_cycle[6]["inBedAt"].startswith("2026-05-03T21:30")
    assert by_cycle[5]["lightsOutAt"].startswith("2026-05-03T23:30")
    assert by_cycle[4]["lightsOutAt"].startswith("2026-05-04T01:00")

    summary = summarize_week(
        [
            {"date": "2026-04-27", "actualCycles": 5, "plannedCycles": 6},
            {"date": "2026-04-28", "actualCycles": 4},
            {"date": "2026-05-01", "actualCycles": 6},
        ],
        week_start=date(2026, 4, 27),
    )
    assert summary["actualCycles"] == 15
    assert summary["cyclesToTarget"] == 20
    assert summary["cyclesToMinimum"] == 13
    assert summary["status"] == "below_minimum"
    return {"ok": True, "tests": ["windows", "weekly"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="R90 sleep planning calculator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    windows = subparsers.add_parser("windows", help="calculate bedtime windows")
    windows.add_argument("--wake-time", required=True, help="target wake time as HH:mm")
    windows.add_argument("--wake-date", help="target wake date as YYYY-MM-DD")
    windows.add_argument("--wind-down", type=int, default=30, help="wind-down minutes, 0..120")
    windows.add_argument("--cycles", help="comma-separated cycle counts, default 4,5,6")
    windows.add_argument("--timezone", help="IANA timezone, e.g. Asia/Shanghai")
    windows.set_defaults(func=cmd_windows)

    weekly = subparsers.add_parser("weekly", help="summarize weekly R90 logs")
    weekly.add_argument("--week-start", required=True, help="week start as YYYY-MM-DD")
    weekly.add_argument("--entries-file", help="JSON file containing sleep log entries")
    weekly.add_argument("--entries-json", help="JSON array containing sleep log entries")
    weekly.add_argument("--target", type=int, default=35, help="weekly target cycles")
    weekly.set_defaults(func=cmd_weekly)

    self_test = subparsers.add_parser("self-test", help="run built-in validation")
    self_test.set_defaults(func=cmd_self_test)
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
