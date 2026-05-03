---
name: r90_sleep_planner
description: Calculate R90 bedtime windows from a target wake time and summarize weekly R90 sleep-cycle logs with conservative wellness guidance.
---

# R90 Sleep Planner

Use this skill when the user asks about R90 sleep planning, 90-minute sleep cycles, bedtime windows from a wake target, or weekly R90 completion tracking.

R90 is planning guidance, not medical advice. Do not diagnose, treat, or promise sleep quality. If the user describes severe insomnia, suspected sleep apnea, long-term fatigue, or health risk, recommend professional help.

## Workflow

1. Identify the task:
   - Bedtime windows: calculate 4, 5, and 6 cycle options unless the user gives cycle counts.
   - Weekly tracking: summarize actual R90 cycles completed this week against a target.
2. Use the bundled script for arithmetic whenever tools are available. Resolve script paths relative to this skill directory.
3. If required inputs are missing, ask only for the missing core input:
   - Bedtime windows require `wakeTime` in `HH:mm`.
   - Weekly tracking requires dated entries with `actualCycles`.
4. Defaults:
   - `cycleOptions`: `[4, 5, 6]`
   - `windDownMinutes`: `30`
   - `targetCycles`: `35`
   - `minimumUsefulRange`: `[28, 30]`
   - `timezone`: device/local timezone unless the user gives an IANA timezone.
5. Present results in the user's language. For Chinese users, use concise Chinese labels.

## Script Usage

Calculate bedtime windows:

```bash
python3 scripts/r90_calc.py windows --wake-time 07:00 --wake-date 2026-05-04 --wind-down 30 --cycles 4,5,6 --timezone Asia/Shanghai
```

Summarize a week from a JSON file:

```bash
python3 scripts/r90_calc.py weekly --week-start 2026-04-27 --entries-file sleep-log.json --target 35
```

Run built-in validation:

```bash
python3 scripts/r90_calc.py self-test
```

## Response Shape

For bedtime windows, include:

- wake target
- wind-down buffer
- each option's cycle count, sleep duration, in-bed time, lights-out time, and rollover notes
- a short non-clinical disclaimer

For weekly tracking, include:

- actual R90 cycles completed
- target cycles and gap
- whether the total is below the minimum useful range
- 7-day breakdown when available
- one practical planning suggestion, not a medical claim

## Data Contract

Read `references/data_contracts.md` if you need exact field names or storage guidance.
