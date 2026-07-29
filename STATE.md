# State

## Current stage
maintenance

## Working now

- Use this repository as the single source of truth for R90.
- Keep deterministic calculation in `r90_calc.py`.
- Maintain portable skill behavior and host adapters for Codex, OpenClaw, MiClaw, and SLI.
- Keep the three core usage scenes covered by acceptance checks.

## Current shape

- GitHub-backed repository and MIT license exist.
- Skill implementation lives under `skills/r90-sleep-planner/`.
- CLI supports bedtime windows, wake suggestions, direct recording, check-in parsing, weekly summaries, and self-test.
- Adapter references exist for Codex, OpenClaw, MiClaw, SLI, and shared data contracts.
- Product-promo video assets remain under `videos/r90-product-promo/`.

## Risks

- Users may treat R90 cycle math as medical advice or a sleep-quality guarantee.
- Host products vary in whether they can execute scripts, store local logs, or send actual notifications.
- "Alarm" wording can overpromise if the host only supports chat reminders.
- Morning check-ins can duplicate records unless they upsert by the prompted sleep date.
- Installed host copies can drift from the repository unless deployment is explicit.

## Next steps

1. Run `python3 skills/r90-sleep-planner/scripts/r90_calc.py self-test` after behavior changes.
2. Smoke-test the three core prompts in the target host.
3. Sync the repository skill to installed host copies only when requested.
4. Keep host reminders separate from calculation logic.

## Done when

- `self-test` passes.
- `我明天 8 点起` returns all 6/5/4 bedtime windows.
- `我现在要睡了` uses current local time and returns wake options.
- `5` and `23:30-07:00` both produce one idempotent sleep-date entry and update the weekly KPI.
