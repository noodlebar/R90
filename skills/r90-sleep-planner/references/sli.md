# SLI Adapter

Use this reference only when installing or wiring R90 inside an SLI-style host that can register skill instructions and expose host actions.

## Placement

Register this file as the user-facing skill body:

```text
skills/r90-sleep-planner/SKILL.md
```

If SLI supports bundled resources, include:

```text
skills/r90-sleep-planner/scripts/r90_calc.py
skills/r90-sleep-planner/references/data_contracts.md
```

If SLI only supports a single instruction body, register the `SKILL.md` contents and rely on the manual fallback algorithms in that file.

## Host Actions

Expose these actions when possible:

```text
r90.windows(wakeTime, wakeDate, windDownMinutes=30, cycleOptions=[4,5,6], timezone)
r90.wake(now=true | sleepTime, sleepDate, cycleOptions=[4,5,6], timezone)
r90.checkin(reply, date=yesterday, store="~/.r90/sleep-log.json", timezone)
r90.weekly(weekStart, entriesFile | entriesJson, target=35)
```

The action contract must match `references/data_contracts.md`.

## Daily Check-in

SLI reminder delivery is host-owned. The skill supplies message text and parsing behavior.

Recommended prompt:

```text
早，记一下昨晚睡眠。
直接回周期数：5
记不清就回时间段：23:30-07:00
不记回：跳过
```

When the user replies, call `r90.checkin` with:

- `date`: previous local calendar date, unless the reminder thread carries an explicit prompted date.
- `reply`: the user's raw reply.
- `store`: private local storage or `~/.r90/sleep-log.json`.
- `timezone`: host or user timezone.

## Response Rules

- Render user-facing results as plain text.
- Keep raw JSON for tool state, logs, or debugging.
- Do not claim that a native alarm was created unless SLI exposes a real alarm action and the user approved it.
- If no persistent store is available, say the cycles were calculated but not saved.
