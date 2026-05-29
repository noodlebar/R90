---
name: r90_sleep_planner
description: Calculate R90 bedtime windows, recommend wake times from lights-out, and record weekly R90 sleep-cycle logs with conservative wellness guidance.
---

# R90 Sleep Planner

Use this skill when the user asks about R90 sleep planning, 90-minute sleep cycles, bedtime windows from a wake target, wake-time suggestions from "I am going to sleep now", low-friction daily R90 check-ins, or weekly R90 completion tracking.

R90 is planning guidance, not medical advice. Do not diagnose, treat, or promise sleep quality. If the user describes severe insomnia, suspected sleep apnea, long-term fatigue, or health risk, recommend professional help.

Support both Chinese and English. Reply in the user's language. If the user mixes languages, prefer the language of the latest request.

## Workflow

1. Identify the task:
   - Bedtime windows: when the user says a wake target such as `我明天9点起床` or `I need to wake up at 9 tomorrow`, calculate and show all 4, 5, and 6 cycle options unless the user gives cycle counts.
   - Wake suggestions: when the user says they are going to sleep now, such as `我要睡了` or `I am going to sleep now`, calculate wake options by adding 4, 5, and 6 R90 cycles to the current local time.
   - Daily check-in: ask for the easiest possible reply, then parse and record it for the prompted sleep date.
   - Weekly tracking: summarize actual R90 cycles completed this week against a target.
2. Prefer deterministic tools for arithmetic whenever available. First try the bundled script, resolved relative to this skill directory. If the script or shell tool is unavailable, use the manual fallback algorithm in this file and say the result was calculated without the script.
3. If required inputs are missing, ask only for the missing core input:
   - Bedtime windows require `wakeTime` in `HH:mm`.
   - Wake suggestions must use the current local time when the user says "now", "我要睡了", "准备睡了", or similar; otherwise ask for `sleepTime` in `HH:mm`.
   - Daily check-ins should ask only for approximate sleep and wake times. Prefer replies like `23:30-07:00`.
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
7. Daily check-ins are idempotent by sleep date. If the user answers the same morning reminder more than once, update the same prompted date instead of creating a new record for the current date.
8. Never answer "我要睡了" by reusing a previously calculated bedtime window such as `21:30`. That phrase means the user's lights-out time is now.
9. Never answer a wake-target shortcut with only one recommendation. Always show the different cycle bedtime windows.
10. For platform-specific scheduling or delivery behavior, read the relevant adapter reference only when needed:
    - OpenClaw: `references/openclaw.md`
    - Codex: `references/codex.md`
    - MiClaw: `references/miclaw.md`

## Calculation Priority and Fallback

Use this order:

1. Bundled script: `python3 scripts/r90_calc.py ...`
2. Host action/tool that exposes the same `windows`, `wake`, `checkin`, `record`, or `weekly` contract.
3. Manual fallback algorithm below.

Do not fail just because the script cannot be called. If using the fallback, keep the response concise and include a short note such as `脚本不可用，已按 R90 规则直接计算。` or `Script unavailable; calculated directly from the R90 rules.`

Manual fallback constants:

- One R90 cycle is exactly 90 minutes.
- Default cycle options are 4, 5, and 6.
- Default wind-down is 30 minutes.
- Default weekly target is 35 cycles.
- Use the device/local timezone unless the user gives a timezone.

Manual bedtime-window algorithm:

1. Parse the wake target into local `wakeDate` and `wakeTime` in `HH:mm`.
2. For each cycle count, usually 6, 5, then 4:
   - `sleepMinutes = cycleCount * 90`
   - `lightsOutAt = wakeDate wakeTime - sleepMinutes`
   - `inBedAt = lightsOutAt - windDownMinutes`
3. Show the date only when the result crosses a calendar day or the date matters.
4. Always show all default 4/5/6 options unless the user explicitly requested different cycles.

Manual going-to-sleep algorithm:

1. Treat `我要睡了`, `准备睡觉`, `I am going to sleep now`, and similar as lights-out now.
2. Use the current local date and time as `lightsOutAt`; never reuse an earlier recommendation.
3. For each cycle count, usually 4, 5, then 6:
   - `wakeAt = lightsOutAt + cycleCount * 90 minutes`
4. Show the reference lights-out time and the 4/5/6 wake options.

Manual check-in parsing algorithm:

1. If the reply means skip, such as `跳过`, `skip`, or `不记`, mark the check-in skipped.
2. If the reply has a sleep/wake range such as `23:30-07:00`, `23:30 到 07:00`, `11点半到7点`, or `12点-7点`, parse the first time as sleep and the second as wake.
3. If wake time is earlier than sleep time, treat wake as the next calendar day.
4. For ambiguous morning replies where both times are 1-12 and the raw duration is more than 12 hours, treat the first time as evening when that yields a duration of 12 hours or less. Examples: `11点-7点` means `23:00-07:00`; `12点-7点` means `00:00-07:00`.
5. `actualCycles = floor(durationMinutes / 90)`, clamped to 0 through 7.
6. If the user gives duration directly, such as `睡了7.5h`, convert hours to minutes and apply the same cycle formula.
7. If the user gives a cycle count directly, such as `5` or `5 cycles`, use that count.
8. If no persistent store is available, report the parsed cycles without claiming the record was saved.

## Wake-target Shortcut Flow

When the user says `我明天9点起床`, `明早7点醒`, `明天 09:00 起`, `I need to wake up at 9 tomorrow`, `wake me at 7 tomorrow`, or similar:

1. Interpret it as a bedtime-window request.
2. Convert Chinese time to `HH:mm`, for example `9点` -> `09:00`.
3. Use tomorrow's local date when the user says `明天`, `明早`, `tomorrow`, or `tomorrow morning`.
4. Call the bundled script with `windows` if available; otherwise use the manual bedtime-window algorithm.
5. Show all 4, 5, and 6 cycle options, not just the longest or recommended option.
6. Do not add a long explanation. Do not say only `23:30 就寝`.

Preferred Chinese response shape:

```text
明天 09:00 起床的话：

6 周期：00:00 熄灯（9小时）
5 周期：01:30 熄灯（7.5小时）
4 周期：03:00 熄灯（6小时）

如果提前放松 30 分钟，上床时间分别是 23:30 / 01:00 / 02:30。
```

If `windDownMinutes` is nonzero, include both `熄灯` and a compact `上床` line. If the user asks for "睡觉时间", treat `lightsOutAt` as the primary time and `inBedAt` as the wind-down time.

Preferred English response shape:

```text
For a 09:00 wake-up tomorrow:

6 cycles: lights out at 00:00 (9h)
5 cycles: lights out at 01:30 (7.5h)
4 cycles: lights out at 03:00 (6h)

With a 30-minute wind-down, start winding down at 23:30 / 01:00 / 02:30.
```

## Going-to-sleep Flow

When the user says `我要睡了`, `我现在睡了`, `准备睡觉`, `I am going to sleep now`, `going to bed now`, or similar:

1. Do not manually calculate from memory.
2. Do not use a previous bedtime recommendation as lights-out.
3. Call the bundled script with `wake --now` if available; otherwise use the manual going-to-sleep algorithm.
4. Present the actual reference `lightsOutAt`.

## Morning Check-in UX

Daily reminder output must be plain text. Never wrap the reminder in JSON, do not output `{"text": "..."}`, and do not use a code block.

Use this prompt style for daily reminders:

```text
早，记一下昨晚睡眠。
大约几点睡、几点醒？直接回：23:30-07:00
不记就回：跳过
```

English reminder style:

```text
Morning check-in.
What time did you roughly fall asleep and wake up?
Reply like: 23:30-07:00
Reply skip to skip.
```

Avoid this style:

```text
昨晚你完成了几个完整的 R90 睡眠周期？
```

Reason: the user should not need to know or calculate R90 cycles in the morning. Ask for approximate sleep and wake times, parse the time range, then explain the recorded R90 count after saving it.

Date rule:

- A 10:00 morning check-in records the previous local calendar date by default.
- If the reminder was for `5月2日`, every reply in that reminder thread updates `2026-05-02`, even if the user replies later on `5月3日`.
- Do not record today's date from a morning check-in unless the user explicitly says the sleep belongs to today.
- If a record already exists for the target date, treat the new reply as a correction and say `已更新`, not `已新增`.

## Script Usage

Calculate bedtime windows:

```bash
python3 scripts/r90_calc.py windows --wake-time 07:00 --wake-date 2026-05-04 --wind-down 30 --cycles 4,5,6 --timezone Asia/Shanghai
```

Shortcut example for `我明天9点起床`:

```bash
python3 scripts/r90_calc.py windows --wake-time 09:00 --wake-date <tomorrow-local-date> --wind-down 30 --cycles 4,5,6 --timezone Asia/Shanghai
```

Calculate wake suggestions from a lights-out time:

```bash
python3 scripts/r90_calc.py wake --sleep-time 23:30 --sleep-date 2026-05-03 --cycles 4,5,6 --timezone Asia/Shanghai
```

When the user says "I am going to sleep now", omit `--sleep-time` and use the local current time:

```bash
python3 scripts/r90_calc.py wake --now --cycles 4,5,6 --timezone Asia/Shanghai
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

For platform-specific scheduling, reminders, or message delivery, read only the relevant adapter reference under `references/`.

Run built-in validation:

```bash
python3 scripts/r90_calc.py self-test
```

## Response Shape

For bedtime windows, include:

- wake target
- wind-down buffer
- all 4/5/6 options by default
- each option's cycle count, sleep duration, lights-out time, in-bed time when wind-down applies, and rollover notes
- a short non-clinical disclaimer

For wake suggestions, include:

- lights-out time
- whether the lights-out time came from current time or a provided time
- 4/5/6 cycle wake options
- total sleep duration per option
- note that this is not a system alarm
- if the host can set reminders, ask before creating any reminder or alarm

For daily check-ins, include:

- date recorded
- whether the entry was created or updated
- actual R90 cycles
- sleep duration from the parsed reply when available, using `sleepDurationDisplay` or exact hours such as `8.25h`; do not round `8.25h` to `8.2h`
- source used to infer cycles, normally the sleep/wake time range
- updated weekly total and gap
- where the record was stored when relevant
- only the final result; do not expose internal arithmetic, implementation notes, or phrases like `脚本用了 round()` / `我来修一下`

For weekly tracking, include:

- actual R90 cycles completed
- target cycles and gap
- whether the total is below the minimum useful range
- 7-day breakdown when available
- one practical planning suggestion, not a medical claim

## Data Contract

Read `references/data_contracts.md` if you need exact field names or storage guidance. Read platform adapter references only when the user asks to install, schedule, or troubleshoot this skill on that host.
