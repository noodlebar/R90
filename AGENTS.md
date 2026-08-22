# Agents

## Default roles

- Lead Agent: reads project memory, defines acceptance, and owns final integration.
- Skill Builder: edits `skills/r90-sleep-planner/SKILL.md`, shared references, and response behavior.
- Calculator Builder: edits `skills/r90-sleep-planner/scripts/r90_calc.py` and owns deterministic tests.
- Adapter Builder: edits one host reference at a time: Codex, OpenClaw, MiClaw, or SLI.
- Reviewer Agent: checks regressions, health/safety wording, and missing validation.

## Ownership rules

- Split work by file ownership, not vague feature names.
- Do not edit host adapter docs and calculator logic in the same subtask unless the behavior contract also changes.
- Do not change storage shape without updating `DATA-CONTRACTS.md` and `skills/r90-sleep-planner/references/data_contracts.md`.
- Keep release actions owned by one lead agent.
