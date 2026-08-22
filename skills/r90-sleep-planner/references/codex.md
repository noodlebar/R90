# Codex Adapter

Use this reference only when installing, testing, or scheduling R90 in Codex-style environments.

## Placement

Recommended local skill placement:

```text
$CODEX_HOME/skills/r90-sleep-planner/
```

For project-local development, keep the skill under:

```text
<workspace>/skills/r90-sleep-planner/
```

## Execution

Use the bundled script directly for deterministic math:

```bash
python3 -B scripts/r90_calc.py self-test
python3 -B scripts/r90_calc.py windows --wake-time 09:00 --wake-date 2026-05-04 --wind-down 30 --timezone Asia/Shanghai
python3 -B scripts/r90_calc.py wake --now --timezone Asia/Shanghai
python3 -B scripts/r90_calc.py checkin --reply "23:30-07:00" --date 2026-05-02 --store ~/.r90/sleep-log.json --timezone Asia/Shanghai
```

Resolve `scripts/r90_calc.py` relative to the skill directory.

## Scheduling

If Codex provides automations or reminders, use the host automation capability to send this plain-text reminder:

```text
早，记一下昨晚睡眠。
直接回周期数：5
记不清就回时间段：23:30-07:00
不记回：跳过
```

The automation should not write records by itself. It should prompt the user, then call `checkin` after the user replies. Record the previous local calendar date unless the user explicitly gives another date.

## Safety

- Do not use native alarm language unless Codex exposes a real alarm/notification tool.
- Keep logs local unless the user explicitly asks for sync/export.
- If shell execution is unavailable, the agent may follow the workflow manually, but it must be explicit that calculations were not script-verified.
