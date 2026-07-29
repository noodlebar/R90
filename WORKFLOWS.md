# Workflows

## Build

1. Read `STATE.md`, `SAFEGUARDS.md`, and `DECISIONS.md`.
2. Edit the skill body or the adapter reference for the requested host.
3. Keep shared calculation behavior in `skills/r90-sleep-planner/scripts/r90_calc.py`.
4. Update both data-contract documents when fields or storage semantics change.
5. Run the deterministic validation and relevant smoke tests.

## Skill Release QA

Run:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py self-test
python3 skills/r90-sleep-planner/scripts/r90_calc.py windows --wake-time 08:00 --wake-date 2026-05-10 --timezone Asia/Shanghai
python3 skills/r90-sleep-planner/scripts/r90_calc.py wake --sleep-time 23:30 --sleep-date 2026-05-09 --timezone Asia/Shanghai
python3 skills/r90-sleep-planner/scripts/r90_calc.py checkin --reply "23:30-07:00" --date 2026-05-08 --store /tmp/r90-sleep-planner-log.json --timezone Asia/Shanghai
```

Acceptance:

- `self-test` returns `"ok": true`.
- `windows` returns 23:00 / 00:30 / 02:00 lights-out for an 08:00 wake target.
- `wake` returns 05:30 / 07:00 / 08:30 for a 23:30 lights-out target.
- `checkin` parses 5 full cycles.

## Adapter Changes

- Codex-specific behavior belongs in `references/codex.md`.
- OpenClaw-specific behavior belongs in `references/openclaw.md`.
- MiClaw-specific behavior belongs in `references/miclaw.md`.
- SLI host/tool behavior belongs in `references/sli.md`.
- Keep the top-level `SKILL.md` portable and retain manual fallback algorithms.

## Reminder Setup

The skill does not schedule itself. The host creates a daily reminder and passes replies back to the skill.

Reminder output must be plain text:

```text
早，记一下昨晚睡眠。
直接回周期数：5
记不清就回时间段：23:30-07:00
不记回：跳过
```

## Maintenance Rule

If a task repeats twice, document it here or turn it into a deterministic script.
