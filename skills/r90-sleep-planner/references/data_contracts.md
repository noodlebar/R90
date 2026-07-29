# R90 Data Contracts

## SleepPlanInput

- `wakeTime`: required local time, `HH:mm`
- `wakeDate`: optional local date, `YYYY-MM-DD`
- `cycleOptions`: integer array, default `[4, 5, 6]`
- `windDownMinutes`: integer, default `30`, allowed `0..120`
- `timezone`: optional IANA timezone string, default device/local timezone

Wake-target shortcuts such as `我明天9点起床` must be treated as `SleepPlanInput`, not as a single recommendation. Show all default cycle options.

## SleepWindow

- `cycleCount`: integer
- `sleepMinutes`: `cycleCount * 90`
- `inBedAt`: local datetime
- `lightsOutAt`: local datetime
- `wakeAt`: local datetime
- `label`: short display label
- `notes`: rollover, timezone, or safety notes

## WakeOption

- `cycleCount`: integer
- `sleepMinutes`: `cycleCount * 90`
- `lightsOutAt`: local datetime
- `wakeAt`: local datetime
- `label`: short display label
- `notes`: next-day, timezone, reminder, or safety notes

When the user says they are going to sleep now, `lightsOutAt` must be the current local time. Do not reuse a previous bedtime window.

## SleepLogEntry

- `date`: required local date, `YYYY-MM-DD`
- `actualCycles`: integer, recommended `0..7`
- `plannedCycles`: optional integer
- `note`: optional string
- `updatedAt`: optional ISO datetime

Same-date writes must be upserts. There must be at most one `SleepLogEntry` per `date` in the local store.

## CheckInReply

Accepted low-friction formats:

- preferred sleep range: `23:30-07:00`, `23:30 到 07:00`
- exact cycle count: `5`, `5个`, `5 cycles`
- duration: `7.5h`, `睡了7.5小时`
- skip: `跳过`, `稍后`, `skip`

For morning reminders, accept a direct cycle count when known and a time range when the user does not want to calculate cycles.

When parsing duration or sleep range, convert completed cycles with floor division: `sleepMinutes // 90`, capped to `0..7`.

## WeeklyCycleSummary

- `weekStart`: local date, `YYYY-MM-DD`
- `weekEnd`: local date, `YYYY-MM-DD`
- `actualCycles`: sum of `actualCycles`
- `plannedCycles`: sum of present `plannedCycles`
- `targetCycles`: default `35`
- `cyclesToTarget`: max of `targetCycles - actualCycles` and `0`
- `minimumUsefulRange`: default `[28, 30]`
- `cyclesToMinimum`: max of `minimumUsefulRange[0] - actualCycles` and `0`
- `days`: seven daily rows

## Storage Guidance

For V1, store logs locally on the user's device or in the host product's private memory/file store. Do not upload sleep logs by default. If the host product asks where to store data, prefer a local JSON file or private local memory.

Default local file store for CLI-capable hosts:

- `~/.r90/sleep-log.json`
- format: JSON array of `SleepLogEntry`
- same-date records are updated in place, not duplicated

## Scheduling Guidance

The skill does not schedule work by itself. Treat scheduled messages as host capabilities. Do not describe them as native alarms unless the host exposes a real alarm or notification tool.

Reminder delivery should be plain text unless the host explicitly requires a structured payload.

Recommended reminder copy:

```text
早，记一下昨晚睡眠。
直接回周期数：5
记不清就回时间段：23:30-07:00
不记回：跳过
```

Date rule:

- Morning check-ins record the previous local calendar date by default.
- A reply in the same reminder thread updates the same prompted sleep date.
- Do not create a current-date record from a repeated reply unless the user explicitly asks to record today.

Permission boundary:

- Skill code can parse and record check-ins, but cannot grant channel send permission.
- If external delivery reports `unauthorized` or `Forbidden`, fix host channel credentials, bot permissions, or target identifiers.
