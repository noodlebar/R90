---
name: r90_sleep_planner
description: Calculate R90 bedtime windows, recommend wake times from lights-out, and record weekly R90 sleep-cycle logs with conservative wellness guidance.
---

# R90 Sleep Planner

Use this skill when the user asks about R90 sleep planning, 90-minute sleep cycles, bedtime windows from a wake target, wake-time suggestions from "I am going to sleep now", low-friction daily R90 check-ins, or weekly R90 completion tracking.

R90 is planning guidance, not medical advice. Do not diagnose, treat, or promise sleep quality. If the user describes severe insomnia, suspected sleep apnea, long-term fatigue, or health risk, recommend professional help.

## Workflow

1. Identify the task:
   - Bedtime windows: calculate 4, 5, and 6 cycle options unless the user gives cycle counts.
   - Wake suggestions: when the user says they are going to sleep now, calculate wake options by adding 4, 5, and 6 R90 cycles to the lights-out time.
   - Daily check-in: ask for the easiest possible reply, then parse and record it for yesterday or a specified date.
   - Weekly tracking: summarize actual R90 cycles completed this week against a target.
2. Use the bundled script for arithmetic whenever tools are available. Resolve script paths relative to this skill directory.
3. If required inputs are missing, ask only for the missing core input:
   - Bedtime windows require `wakeTime` in `HH:mm`.
   - Wake suggestions can use the current local time when the user says "now"; otherwise ask for `sleepTime` in `HH:mm`.
   - Daily check-ins accept `0..7`, a sleep duration such as `7.5h`, or a time range such as `23:30-07:00`.
   - Weekly tracking requires dated entries with `actualCycles`.
4. Defaults:
   - `cycleOptions`: `[4, 5, 6]`
   - `windDownMinutes`: `30`
   - `targetCycles`: `35`
   - `minimumUsefulRange`: `[28, 30]`
   - `timezone`: device/local timezone unless the user gives an IANA timezone.
   - `store`: `~/.r90/sleep-log.json` for local self-reported R90 logs.
5. Present results in the user's language. For Chinese users, use concise Chinese labels and avoid asking them to calculate R90 manually.
6. Do not claim to set a system alarm unless the host product exposes an alarm or notification tool. If only OpenClaw cron is available, describe it as a chat reminder.

## Morning Check-in UX

Use this prompt style for daily reminders:

```text
早。昨晚睡得怎么样？
直接回：5 / 7.5h / 23:30-07:00 / 跳过
```

Avoid this style:

```text
昨晚你完成了几个完整的 R90 睡眠周期？
```

Reason: the user should not need to know or calculate R90 cycles in the morning. Parse their simple reply, then explain the recorded result after saving it.

## Script Usage

Calculate bedtime windows:

```bash
python3 scripts/r90_calc.py windows --wake-time 07:00 --wake-date 2026-05-04 --wind-down 30 --cycles 4,5,6 --timezone Asia/Shanghai
```

Calculate wake suggestions from a lights-out time:

```bash
python3 scripts/r90_calc.py wake --sleep-time 23:30 --sleep-date 2026-05-03 --cycles 4,5,6 --timezone Asia/Shanghai
```

When the user says "I am going to sleep now", omit `--sleep-time` and use the local current time:

```bash
python3 scripts/r90_calc.py wake --cycles 4,5,6 --timezone Asia/Shanghai
```

Record a daily self-reported check-in and return the updated weekly summary:

```bash
python3 scripts/r90_calc.py record --date 2026-05-02 --actual-cycles 5 --store ~/.r90/sleep-log.json --timezone Asia/Shanghai
```

Parse a low-friction daily check-in reply and record it:

```bash
python3 scripts/r90_calc.py checkin --reply "23:30-07:00" --date 2026-05-02 --store ~/.r90/sleep-log.json --timezone Asia/Shanghai
```

Summarize a week from a JSON file:

```bash
python3 scripts/r90_calc.py weekly --week-start 2026-04-27 --entries-file sleep-log.json --target 35
```

Create a daily OpenClaw chat reminder outside the skill:

```bash
openclaw cron add --name "R90 morning check-in" --cron "0 10 * * *" --tz "Asia/Shanghai" --session main --system-event "R90 morning check-in: ask the user how many R90 cycles they completed yesterday. If they answer 0-7, use the r90_sleep_planner skill record flow and then report the updated weekly summary." --wake now
```

Better low-friction cron prompt:

```bash
openclaw cron add --name "R90 morning check-in" --cron "0 10 * * *" --tz "Asia/Shanghai" --session main --system-event "R90 morning check-in. Send exactly this concise prompt in Chinese: 早。昨晚睡得怎么样？直接回：5 / 7.5h / 23:30-07:00 / 跳过. When the user replies, use r90_sleep_planner checkin parsing. Record parsed cycles for yesterday, then respond with the updated weekly total in one short sentence." --wake now
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

For wake suggestions, include:

- lights-out time
- 4/5/6 cycle wake options
- total sleep duration per option
- note that this is not a system alarm
- if the host can set reminders, ask before creating any reminder or alarm

For daily check-ins, include:

- date recorded
- actual R90 cycles
- source used to infer cycles when helpful, for example time range or duration
- updated weekly total and gap
- where the record was stored when relevant

For weekly tracking, include:

- actual R90 cycles completed
- target cycles and gap
- whether the total is below the minimum useful range
- 7-day breakdown when available
- one practical planning suggestion, not a medical claim

## Data Contract

Read `references/data_contracts.md` if you need exact field names or storage guidance.
