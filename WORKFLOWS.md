# Workflows

## Recurring tasks

- 功能规划
- 本地实现
- release QA
- 文档和状态回填

## Calculator implementation workflow

1. Confirm the input contract in `DATA-CONTRACTS.md`.
2. Implement or update the pure time-calculation function first.
3. Add tests for midnight rollover, default cycles, and wind-down buffer.
4. Build UI around the tested function.
5. Run local smoke test and update `STATE.md`.

## Rule

If a task repeats twice, document it here or turn it into a script.
