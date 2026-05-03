# MiClaw Adapter

Use this reference only when installing, testing, or scheduling R90 in MiClaw or a MiClaw-like host.

## Compatibility Model

R90 requires only:

- ability to read `SKILL.md`
- ability to execute `python3 scripts/r90_calc.py`, or an equivalent tool bridge
- optional local/private storage for `~/.r90/sleep-log.json`
- optional host reminder capability for morning check-ins

If MiClaw does not support `SKILL.md` discovery, register the skill body as a system/tool instruction and expose `scripts/r90_calc.py` as a callable local tool.

## Tool Contract

Expose these script commands as MiClaw actions if possible:

```text
r90.windows(wakeTime, wakeDate, windDownMinutes=30, cycleOptions=[4,5,6], timezone)
r90.wake(now=true | sleepTime, sleepDate, cycleOptions=[4,5,6], timezone)
r90.checkin(reply, date=yesterday, store="~/.r90/sleep-log.json", timezone)
r90.weekly(weekStart, entriesFile | entriesJson, target=35)
```

All outputs are JSON. The host should render user-facing responses in plain text, not expose raw JSON unless debugging.

## Reminder UX

Preferred reminder text:

```text
早，记一下昨晚睡眠。
大约几点睡、几点醒？直接回：23:30-07:00
不记就回：跳过
```

When the user replies, call `r90.checkin` for the prompted sleep date. Repeated replies in the same reminder thread should update the same date, not create a new current-date record.

## Permissions

MiClaw host code owns message delivery, notifications, and alarm permissions. The R90 skill cannot grant these. If a push fails, debug MiClaw channel credentials, bot scopes, or target identifiers before changing R90 logic.
