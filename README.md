# R90

R90 sleep-window calculator for planning bedtime windows from wake targets using Nick Littlehales' 90-minute cycle method.

## Product intent

R90 helps users plan practical bedtime windows from a fixed wake target. Instead of asking "how many hours should I sleep tonight?", the app counts backwards in 90-minute recovery cycles and presents a small set of bedtime options that fit the user's next morning.

The first version is a local utility calculator, not a medical sleep diagnosis product.

## R90 method assumptions

- A sleep cycle is planned as a 90-minute block.
- The wake time is the anchor; bedtime windows are calculated backwards from it.
- Users compare nights by cycle count, with weekly totals as the larger view.
- The calculator should make 4, 5, and 6 cycle options easy to scan.
- Optional pre-sleep wind-down time is separate from the sleep cycle math.

## First shipping outcome

A single-screen calculator that lets a user enter:

- target wake time
- desired cycle count or recommended options
- optional wind-down buffer
- timezone or local-device time handling

It returns:

- recommended in-bed time
- lights-out time
- total planned sleep duration
- cycle count
- weekly cycle impact
- a clear note that this is planning guidance, not clinical advice

## Codex 启动顺序

1. 先读本文件，理解项目目标、范围和当前结构。
2. 再读 `STATE.md`，确认当前阶段、风险和下一步。
3. 再读 `SAFEGUARDS.md` 和 `codex/MODES.md`，确认当前任务属于 `Explore`、`Build` 还是 `Release`。
4. 再读 `DECISIONS.md`，避免重复推翻已有方向。
5. 再读 `WORKFLOWS.md`，按既有流程推进。
6. 再进入实际代码、数据、素材或脚本目录。
7. 最后按需读 `DATA-CONTRACTS.md`、`USER-FLOWS.md`。
8. 再读 `AGENTS.md`，确认角色和写入边界。

## Project Memory

- `STATE.md`: 当前阶段、风险和下一步
- `SAFEGUARDS.md`: 默认安全边界和验证底线
- `DECISIONS.md`: 关键项目决策
- `WORKFLOWS.md`: 复用工作流
- `codex/MODES.md`: `Explore / Build / Release` 模式定义
- `DATA-CONTRACTS.md`: 领域专项运行文档
- `USER-FLOWS.md`: 领域专项运行文档
- `AGENTS.md`: 多 agent 角色和写入边界

## Current shape

- domain: `utility apps`
- product docs for an R90 sleep-window calculator
- data contracts and user flows for first calculator release
- safety boundaries for wellness guidance
- 这个项目遵循 Portfolio OS 运行模型

## Repository layout

- `skills/r90-sleep-planner/`: Codex skill for R90 bedtime windows, wake suggestions, check-ins, and weekly cycle tracking.
- `skills/r90-sleep-planner/scripts/r90_calc.py`: deterministic calculator and local log utility.
- `skills/r90-sleep-planner/references/data_contracts.md`: exact skill-level contracts for generated R90 behavior.
- `DATA-CONTRACTS.md`: product-level input, output, and validation contracts.
- `USER-FLOWS.md`: first calculator flows and edge cases.
- `SAFEGUARDS.md`: health, data, and release boundaries.
- `STATE.md`: current project status and next milestone.

## Local validation

Run the bundled calculator self-test:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py self-test
```

Expected result:

```json
{"ok": true}
```

Try a bedtime-window calculation:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py windows --wake-time 07:00 --wake-date 2026-05-04 --wind-down 30 --cycles 4,5,6 --timezone Asia/Shanghai
```

## Documentation status

The project memory and first calculator contracts are complete for the discovery-stage handoff. Implementation stack, UI language, and weekly-history scope remain open product decisions in `STATE.md`.

## Next steps

1. Choose the implementation stack for the calculator.
2. Build the first local calculator screen and tests.
3. Add examples for common wake times and weekly cycle planning.
