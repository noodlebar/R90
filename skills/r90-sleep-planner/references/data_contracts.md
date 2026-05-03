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
