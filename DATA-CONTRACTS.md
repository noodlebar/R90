# Data Contracts

## Core entities

### SleepPlanInput

- `wakeTime`: local time, required, `HH:mm`
- `wakeDate`: local date, optional for same-day previews, `YYYY-MM-DD`
- `cycleOptions`: integer array, default `[4, 5, 6]`
- `windDownMinutes`: integer, default `30`, allowed `0..120`
- `timezone`: IANA timezone string, optional; default device timezone

### SleepWindow

- `cycleCount`: integer, required
- `sleepMinutes`: integer, always `cycleCount * 90`
- `lightsOutAt`: local datetime, required
- `inBedAt`: local datetime, required, `lightsOutAt - windDownMinutes`
- `wakeAt`: local datetime, required
- `label`: short user-facing label, for example `5 cycles`
- `notes`: string array for rollover or edge-case messages

### WeeklyCycleSummary

- `plannedCycles`: integer, sum of planned cycle counts
- `targetCycles`: integer, default `35`
- `minimumUsefulRange`: integer tuple, default `[28, 30]`
- `days`: array of daily planned cycle counts

## Validation rules

- Never hard-code a universal bedtime; always calculate from the user's wake target.
- Treat wind-down as preparation time, not sleep time.
- Preserve date rollover explicitly when a calculated bedtime falls on the previous calendar day.
- Do not claim the output diagnoses, treats, or guarantees sleep quality.
- Any change to `SleepPlanInput.wakeTime`, `SleepWindow.lightsOutAt`, or `cycleCount` semantics is breaking.
