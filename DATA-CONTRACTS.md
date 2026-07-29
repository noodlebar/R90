# Data Contracts

## Bedtime Windows

Input:

- `wakeTime`: `HH:mm`, 24-hour local time.
- `wakeDate`: `YYYY-MM-DD`.
- `cycleOptions`: integer array, default `[4, 5, 6]`.
- `windDownMinutes`: integer `0..120`, default `30`.
- `timezone`: IANA timezone, default host local timezone.

Output:

- `input`: normalized input fields.
- `windows`: one row per cycle option.
- `disclaimer`: non-medical planning note.

Each window includes:

- `cycleCount`: integer.
- `sleepMinutes`: `cycleCount * 90`.
- `sleepHours`: decimal hours.
- `inBedAt`: ISO local datetime for wind-down start.
- `lightsOutAt`: ISO local datetime for actual sleep target.
- `wakeAt`: ISO local datetime.
- `label`: short display label.
- `notes`: array for previous-day or timezone-transition notes.

## Wake Suggestions

Input:

- `now`: boolean; when true, use current local time as `lightsOutAt`.
- `sleepTime`: optional `HH:mm`; only used when `now` is false.
- `sleepDate`: optional `YYYY-MM-DD`.
- `cycleOptions`: integer array, default `[4, 5, 6]`.
- `timezone`: IANA timezone, default host local timezone.

Output:

- `input.source`: `current_time` or `provided_time`.
- `lightsOutAt`: ISO local datetime.
- `wakeOptions`: rows with `cycleCount`, `sleepMinutes`, `sleepHours`, `lightsOutAt`, `wakeAt`, `label`, and `notes`.
- `disclaimer`: non-medical planning note that does not claim an alarm was created.

## Daily Check-in

Recommended plain-text reminder:

```text
早，记一下昨晚睡眠。
直接回周期数：5
记不清就回时间段：23:30-07:00
不记回：跳过
```

Accepted reply forms:

- Time range: `23:30-07:00`, `23:30 到 07:00`, `11点半到7点`.
- Duration: `睡了7.5h`, `7.5小时`.
- Cycle count: `5`, `5 cycles`, `5个周期`.
- Skip: `跳过`, `不记`, `skip`.

Parsed check-in fields:

- `status`: `parsed`, `skipped`, or `needs_clarification`.
- `actualCycles`: integer `0..7` when parsed.
- `source`: `time_range`, `duration`, or `cycle_count`.
- `sleepMinutes`: parsed or derived sleep duration.
- `normalizedReply`: original reply after outer whitespace is removed.

## Sleep Log

Each stored row includes:

- `date`: sleep date, default previous local calendar date for morning reminders.
- `actualCycles`: integer `0..7`.
- `plannedCycles`: optional integer `0..7`.
- `note`: optional string.
- `updatedAt`: ISO local datetime.

Storage:

- Default local file: `~/.r90/sleep-log.json`.
- Shape: JSON array of dated entries.
- Writes are idempotent by `date`: repeated replies for the same prompted sleep date update the existing entry.
- Sleep logs stay local or in host-private storage unless the user explicitly requests sync or export.

## Weekly KPI

Input:

- `weekStart`: Monday date in `YYYY-MM-DD` unless the host configures another week start.
- `entries`: local JSON entries or host-provided records.
- `target`: default `35`.

Output:

- `weekStart` / `weekEnd`: inclusive seven-day range.
- `actualCycles`: completed cycles in the week.
- `plannedCycles`: sum of present planned values.
- `targetCycles`: target, default `35`.
- `cyclesToTarget`: non-negative target gap.
- `minimumUsefulRange`: default `[28, 30]`.
- `cyclesToMinimum`: non-negative gap to the lower bound.
- `status`: `met_target`, `below_target`, or `below_minimum`.
- `days`: seven daily rows.

## Host Boundary

- The skill calculates, parses, and prepares content.
- Host adapters own notification delivery, native alarm creation, data sync, permissions, and external channel credentials.
- Do not claim a log was saved when persistent storage is unavailable.
- Do not claim a native alarm was created unless the host exposes that capability and the user approved it.

## Breaking Changes

Changes to `wakeTime`, `lightsOutAt`, `cycleCount`, same-date upsert semantics, or the sleep-log storage shape require coordinated updates to this file, the skill-level data contracts, tests, and affected adapters.
