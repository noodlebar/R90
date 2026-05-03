# R90 Data Contracts

## SleepPlanInput

- `wakeTime`: required local time, `HH:mm`
- `wakeDate`: optional local date, `YYYY-MM-DD`
- `cycleOptions`: integer array, default `[4, 5, 6]`
- `windDownMinutes`: integer, default `30`, allowed `0..120`
- `timezone`: optional IANA timezone string, default device/local timezone

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

## SleepLogEntry

- `date`: required local date, `YYYY-MM-DD`
- `actualCycles`: integer, recommended `0..7`
- `plannedCycles`: optional integer
- `note`: optional string
- `updatedAt`: optional ISO datetime

## CheckInReply

Accepted low-friction formats:

- exact cycle count: `5`, `5个`, `5 cycles`
- duration: `7.5h`, `睡了7.5小时`
- sleep range: `23:30-07:00`, `23:30 到 07:00`
- skip: `跳过`, `稍后`, `skip`

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

Default local file store for OpenClaw-style hosts:

- `~/.r90/sleep-log.json`
- format: JSON array of `SleepLogEntry`
- same-date records are updated in place, not duplicated

## Scheduling Guidance

The skill does not schedule work by itself. For OpenClaw, use Gateway cron to ask the user at 10:00 each morning. Treat that as a chat reminder. Do not describe it as a native system alarm.

Recommended reminder copy:

```text
早。昨晚睡得怎么样？
直接回：5 / 7.5h / 23:30-07:00 / 跳过
```
