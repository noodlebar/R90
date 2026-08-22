#!/usr/bin/env python3
"""Deterministic R90 sleep-window and weekly-cycle calculations."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
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

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback.
    fcntl = None  # type: ignore[assignment]


TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
TIME_IN_TEXT_RE = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")
CHINESE_TIME_IN_TEXT_RE = re.compile(r"(?<!\d)([01]?\d|2[0-3])\s*点\s*(半|[0-5]\d\s*分?)?")
SLEEP_DURATION_RE = re.compile(
    r"(?<!\d)(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours|小时|个小时)\b",
    re.IGNORECASE,
)
CYCLE_COUNT_RE = re.compile(r"(?<!\d)([0-7])\s*(?:个|次|cycle|cycles|r90|R90|周期)?(?!\d)")
SKIP_RE = re.compile(r"(skip|pass|later|no\s*record|跳过|略过|稍后|不记|不记录|忘了|不知道)")


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


def time_to_minutes(value: time) -> int:
    return value.hour * 60 + value.minute


def extract_times_from_text(value: str) -> list[time]:
    matches: list[tuple[int, time]] = []
    for match in TIME_IN_TEXT_RE.finditer(value):
        matches.append((match.start(), time(hour=int(match.group(1)), minute=int(match.group(2)))))
    for match in CHINESE_TIME_IN_TEXT_RE.finditer(value):
        minute_text = (match.group(2) or "").replace(" ", "")
        minute = 30 if minute_text == "半" else int(minute_text.replace("分", "") or "0")
        matches.append((match.start(), time(hour=int(match.group(1)), minute=minute)))
    return [item[1] for item in sorted(matches, key=lambda item: item[0])]


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


def add_elapsed(local_dt: datetime, minutes: int) -> datetime:
    if local_dt.tzinfo is None:
        return local_dt + timedelta(minutes=minutes)
    return (local_dt.astimezone(UTC) + timedelta(minutes=minutes)).astimezone(local_dt.tzinfo)


def iso_local(dt: datetime) -> str:
    return dt.isoformat(timespec="minutes")


def local_now(timezone: str | None = None) -> datetime:
    tzinfo = load_tz(timezone)
    return datetime.now(tzinfo)


def monday_for(value: date) -> date:
    return value - timedelta(days=value.weekday())


def cycles_from_minutes(minutes: int) -> int:
    if minutes < 0:
        raise ValueError("sleep minutes cannot be negative")
    return max(0, min(minutes // 90, 7))


def format_duration_minutes(minutes: int) -> str:
    if minutes < 0:
        raise ValueError("duration minutes cannot be negative")
    hours, remainder = divmod(minutes, 60)
    if hours and remainder:
        return f"{hours}小时{remainder}分钟"
    if hours:
        return f"{hours}小时"
    return f"{remainder}分钟"


def parsed_checkin_payload(
    actual_cycles: int,
    source: str,
    sleep_minutes: int,
    normalized_reply: str,
) -> dict[str, Any]:
    return {
        "status": "parsed",
        "actualCycles": actual_cycles,
        "source": source,
        "sleepMinutes": sleep_minutes,
        "sleepHours": round(sleep_minutes / 60, 2),
        "sleepDurationDisplay": format_duration_minutes(sleep_minutes),
        "normalizedReply": normalized_reply,
    }


def sleep_range_minutes(start: time, end: time) -> int:
    start_minutes = time_to_minutes(start)
    end_minutes = time_to_minutes(end)
    duration_minutes = end_minutes - start_minutes
    if duration_minutes < 0:
        duration_minutes += 24 * 60

    # In a morning sleep check-in, "11点-7点" usually means 23:00-07:00,
    # and "12点-7点" usually means 00:00-07:00.
    if duration_minutes > 12 * 60 and 1 <= start.hour <= 12 and 1 <= end.hour <= 12:
        adjusted_start_hour = 0 if start.hour == 12 else start.hour + 12
        adjusted_start = adjusted_start_hour * 60 + start.minute
        adjusted_duration = end_minutes - adjusted_start
        if adjusted_duration < 0:
            adjusted_duration += 24 * 60
        if adjusted_duration <= 12 * 60:
            duration_minutes = adjusted_duration

    return duration_minutes


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


def calculate_wake_options(
    sleep_time: str | None,
    sleep_date: date | None,
    cycle_options: tuple[int, ...],
    timezone: str | None = None,
    use_now: bool = False,
) -> dict[str, Any]:
    tzinfo = load_tz(timezone)
    if use_now:
        lights_out = local_now(timezone)
        source = "current_time"
    elif sleep_time:
        base_date = sleep_date or local_now(timezone).date()
        lights_out = datetime.combine(base_date, parse_hhmm(sleep_time), tzinfo=tzinfo)
        source = "provided_time"
    else:
        lights_out = local_now(timezone)
        source = "current_time"

    options: list[dict[str, Any]] = []
    for cycle_count in sorted(set(cycle_options)):
        sleep_minutes = cycle_count * 90
        wake_at = add_elapsed(lights_out, sleep_minutes)
        notes: list[str] = []

        if wake_at.date() > lights_out.date():
            notes.append("wake time falls on the next calendar day")
        if wake_at.utcoffset() != lights_out.utcoffset():
            notes.append("timezone offset changes between lights-out and wake time")

        options.append(
            {
                "cycleCount": cycle_count,
                "sleepMinutes": sleep_minutes,
                "sleepHours": round(sleep_minutes / 60, 2),
                "label": f"{cycle_count} cycles",
                "lightsOutAt": iso_local(lights_out),
                "wakeAt": iso_local(wake_at),
                "notes": notes,
            }
        )

    return {
        "input": {
            "sleepTime": sleep_time,
            "sleepDate": sleep_date.isoformat() if sleep_date else None,
            "cycleOptions": list(cycle_options),
            "timezone": timezone,
            "source": source,
        },
        "lightsOutAt": iso_local(lights_out),
        "wakeOptions": options,
        "disclaimer": "R90 output is planning guidance, not medical advice or an alarm.",
    }


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


def load_log_store(store_path: Path) -> list[dict[str, Any]]:
    if not store_path.exists():
        return []
    data = json.loads(store_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("sleep log store must contain a JSON array")
    return data


def save_log_store(store_path: Path, entries: list[dict[str, Any]]) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = store_path.with_name(f"{store_path.name}.{os.getpid()}.tmp")
    tmp_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(store_path)


@contextlib.contextmanager
def log_store_lock(store_path: Path):
    lock_path = store_path.with_suffix(store_path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        if fcntl is not None:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def record_sleep_log(
    store_path: Path,
    entry_date: date,
    actual_cycles: int,
    planned_cycles: int | None = None,
    note: str | None = None,
    timezone: str | None = None,
) -> dict[str, Any]:
    if actual_cycles < 0 or actual_cycles > 7:
        raise ValueError("actualCycles must be between 0 and 7")
    if planned_cycles is not None and (planned_cycles < 0 or planned_cycles > 7):
        raise ValueError("plannedCycles must be between 0 and 7")

    with log_store_lock(store_path):
        entries = load_log_store(store_path)
        key = entry_date.isoformat()
        updated_entry = {
            "date": key,
            "actualCycles": actual_cycles,
            "plannedCycles": planned_cycles,
            "note": note,
            "updatedAt": local_now(timezone).isoformat(timespec="seconds"),
        }

        replaced = False
        next_entries: list[dict[str, Any]] = []
        for entry in entries:
            if entry.get("date") == key:
                next_entries.append(updated_entry)
                replaced = True
            else:
                next_entries.append(entry)
        if not replaced:
            next_entries.append(updated_entry)

        next_entries.sort(key=lambda item: str(item.get("date", "")))
        save_log_store(store_path, next_entries)
        return {"entry": updated_entry, "entries": next_entries, "action": "updated" if replaced else "created"}


def parse_checkin_reply(reply: str) -> dict[str, Any]:
    normalized = reply.strip()
    if not normalized:
        return {
            "status": "needs_clarification",
            "reason": "empty reply",
            "acceptedFormats": ["5", "23:30-07:00", "跳过"],
        }
    if SKIP_RE.search(normalized):
        return {"status": "skipped", "reason": "user skipped check-in"}

    times = extract_times_from_text(normalized)
    if len(times) >= 2:
        duration_minutes = sleep_range_minutes(times[0], times[1])
        return parsed_checkin_payload(
            actual_cycles=cycles_from_minutes(duration_minutes),
            source="time_range",
            sleep_minutes=duration_minutes,
            normalized_reply=normalized,
        )

    duration_match = SLEEP_DURATION_RE.search(normalized)
    if duration_match:
        duration_minutes = int(float(duration_match.group(1)) * 60)
        return parsed_checkin_payload(
            actual_cycles=cycles_from_minutes(duration_minutes),
            source="duration",
            sleep_minutes=duration_minutes,
            normalized_reply=normalized,
        )

    cycle_match = CYCLE_COUNT_RE.search(normalized)
    if cycle_match:
        actual_cycles = int(cycle_match.group(1))
        return parsed_checkin_payload(
            actual_cycles=actual_cycles,
            source="cycle_count",
            sleep_minutes=actual_cycles * 90,
            normalized_reply=normalized,
        )

    return {
        "status": "needs_clarification",
        "reason": "reply did not include cycles, duration, or a sleep time range",
        "acceptedFormats": ["5", "23:30-07:00", "跳过"],
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
    entries = read_entries(args)
    return summarize_week(
        entries=entries,
        week_start=parse_date(args.week_start),
        target_cycles=args.target,
    )


def cmd_wake(args: argparse.Namespace) -> dict[str, Any]:
    if args.sleep_date and not args.sleep_time:
        raise ValueError("sleepDate can only be used with sleepTime")
    if args.now and (args.sleep_time or args.sleep_date):
        raise ValueError("now cannot be combined with sleepTime or sleepDate")
    return calculate_wake_options(
        sleep_time=args.sleep_time,
        sleep_date=parse_date(args.sleep_date) if args.sleep_date else None,
        cycle_options=parse_cycles(args.cycles),
        timezone=args.timezone,
        use_now=args.now,
    )


def cmd_record(args: argparse.Namespace) -> dict[str, Any]:
    if args.date:
        entry_date = parse_date(args.date)
    else:
        entry_date = local_now(args.timezone).date() - timedelta(days=1)

    store_path = Path(args.store).expanduser()
    record_result = record_sleep_log(
        store_path=store_path,
        entry_date=entry_date,
        actual_cycles=args.actual_cycles,
        planned_cycles=args.planned_cycles,
        note=args.note,
        timezone=args.timezone,
    )
    week_start = parse_date(args.week_start) if args.week_start else monday_for(entry_date)
    return {
        "store": str(store_path),
        "recorded": record_result["entry"],
        "action": record_result["action"],
        "weeklySummary": summarize_week(
            entries=record_result["entries"],
            week_start=week_start,
            target_cycles=args.target,
        ),
        "disclaimer": "R90 logs are self-reported planning records, not verified sleep measurements.",
    }


def cmd_checkin(args: argparse.Namespace) -> dict[str, Any]:
    parsed = parse_checkin_reply(args.reply)
    if parsed["status"] != "parsed":
        return {
            "checkIn": parsed,
            "prompt": "直接回周期数：5；记不清就回时间段：23:30-07:00；不记回：跳过。",
        }

    if args.date:
        entry_date = parse_date(args.date)
    else:
        entry_date = local_now(args.timezone).date() - timedelta(days=1)

    store_path = Path(args.store).expanduser()
    record_result = record_sleep_log(
        store_path=store_path,
        entry_date=entry_date,
        actual_cycles=int(parsed["actualCycles"]),
        planned_cycles=args.planned_cycles,
        note=args.note,
        timezone=args.timezone,
    )
    week_start = parse_date(args.week_start) if args.week_start else monday_for(entry_date)
    return {
        "checkIn": parsed,
        "store": str(store_path),
        "recorded": record_result["entry"],
        "action": record_result["action"],
        "weeklySummary": summarize_week(
            entries=record_result["entries"],
            week_start=week_start,
            target_cycles=args.target,
        ),
        "disclaimer": "R90 logs are self-reported planning records, not verified sleep measurements.",
    }


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

    wake = calculate_wake_options(
        sleep_time="23:30",
        sleep_date=date(2026, 5, 3),
        cycle_options=(4, 5, 6),
        timezone="Asia/Shanghai",
    )
    by_wake_cycle = {row["cycleCount"]: row for row in wake["wakeOptions"]}
    assert by_wake_cycle[4]["wakeAt"].startswith("2026-05-04T05:30")
    assert by_wake_cycle[5]["wakeAt"].startswith("2026-05-04T07:00")
    assert by_wake_cycle[6]["wakeAt"].startswith("2026-05-04T08:30")
    assert wake["input"]["source"] == "provided_time"

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

    assert parse_checkin_reply("5")["actualCycles"] == 5
    assert parse_checkin_reply("睡了7.5h")["actualCycles"] == 5
    assert parse_checkin_reply("23:30-07:00")["actualCycles"] == 5
    assert parse_checkin_reply("0:00-8:15")["sleepHours"] == 8.25
    assert parse_checkin_reply("0:00-8:15")["sleepDurationDisplay"] == "8小时15分钟"
    assert parse_checkin_reply("11点半到7点")["actualCycles"] == 5
    assert parse_checkin_reply("12点-7点")["actualCycles"] == 4
    assert parse_checkin_reply("跳过")["status"] == "skipped"
    assert parse_checkin_reply("")["acceptedFormats"] == ["5", "23:30-07:00", "跳过"]

    store_path = Path("/tmp/r90_calc_self_test_log.json")
    if store_path.exists():
        store_path.unlink()
    recorded = record_sleep_log(
        store_path=store_path,
        entry_date=date(2026, 5, 1),
        actual_cycles=6,
        planned_cycles=5,
        note="self-test",
        timezone="Asia/Shanghai",
    )
    recorded_again = record_sleep_log(
        store_path=store_path,
        entry_date=date(2026, 5, 1),
        actual_cycles=5,
        planned_cycles=5,
        note="updated",
        timezone="Asia/Shanghai",
    )
    assert len(recorded["entries"]) == 1
    assert recorded["action"] == "created"
    assert recorded_again["action"] == "updated"
    assert recorded_again["entries"][0]["actualCycles"] == 5
    store_path.unlink(missing_ok=True)

    return {"ok": True, "tests": ["windows", "wake", "weekly", "record", "checkin"]}


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

    wake = subparsers.add_parser("wake", help="calculate wake options from a lights-out time")
    wake.add_argument("--sleep-time", help="lights-out time as HH:mm; defaults to current local time")
    wake.add_argument("--sleep-date", help="lights-out date as YYYY-MM-DD")
    wake.add_argument("--now", action="store_true", help="use the current local time as lights-out")
    wake.add_argument("--cycles", help="comma-separated cycle counts, default 4,5,6")
    wake.add_argument("--timezone", help="IANA timezone, e.g. Asia/Shanghai")
    wake.set_defaults(func=cmd_wake)

    record = subparsers.add_parser("record", help="record a self-reported daily R90 log")
    record.add_argument("--date", help="sleep log date as YYYY-MM-DD; defaults to yesterday")
    record.add_argument("--actual-cycles", type=int, required=True, help="actual completed cycles, 0..7")
    record.add_argument("--planned-cycles", type=int, help="planned cycles, 0..7")
    record.add_argument("--note", help="optional short note")
    record.add_argument("--store", default="~/.r90/sleep-log.json", help="local JSON log store")
    record.add_argument("--week-start", help="week start as YYYY-MM-DD; defaults to Monday of the entry week")
    record.add_argument("--target", type=int, default=35, help="weekly target cycles")
    record.add_argument("--timezone", help="IANA timezone, e.g. Asia/Shanghai")
    record.set_defaults(func=cmd_record)

    checkin = subparsers.add_parser("checkin", help="parse a low-friction check-in reply and record it")
    checkin.add_argument("--reply", required=True, help="user reply, preferably 23:30-07:00; skip is accepted")
    checkin.add_argument("--date", help="sleep log date as YYYY-MM-DD; defaults to yesterday")
    checkin.add_argument("--planned-cycles", type=int, help="planned cycles, 0..7")
    checkin.add_argument("--note", help="optional short note")
    checkin.add_argument("--store", default="~/.r90/sleep-log.json", help="local JSON log store")
    checkin.add_argument("--week-start", help="week start as YYYY-MM-DD; defaults to Monday of the entry week")
    checkin.add_argument("--target", type=int, default=35, help="weekly target cycles")
    checkin.add_argument("--timezone", help="IANA timezone, e.g. Asia/Shanghai")
    checkin.set_defaults(func=cmd_checkin)

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
