# R90

## Product Intent / 产品意图

**中文**：R90 是一个可移植的 Agent Skill 和确定性 CLI 工具，用 90 分钟睡眠周期帮助用户围绕目标起床时间规划睡眠窗口，也支持“我要睡了”时反推适合的起床时间，并记录一周完成了多少个 R90 周期。

**English**: R90 is a portable Agent Skill and deterministic CLI utility for planning sleep around 90-minute recovery cycles. It calculates bedtime windows from a target wake time, suggests wake times from a lights-out time, and records lightweight weekly R90 cycle logs.

**安全边界 / Safety Boundary**：R90 只提供睡眠计划和自我记录参考，不是医疗建议；它不诊断睡眠问题、不治疗疾病，也不保证睡眠质量。R90 is planning guidance, not medical advice.

## R90 Method Assumptions / R90 方法假设

- **中文**：一个 R90 周期按 90 分钟计算。  
  **English**: One R90 cycle is treated as a 90-minute block.
- **中文**：起床时间是锚点；睡觉窗口从目标起床时间倒推。  
  **English**: Wake time is the anchor; bedtime windows are calculated backwards from it.
- **中文**：默认展示 4、5、6 个周期，方便用户在睡眠时长和现实安排之间选择。  
  **English**: The default options are 4, 5, and 6 cycles so users can compare practical choices.
- **中文**：`wind-down` 是睡前准备时间，不计入实际睡眠时长。  
  **English**: Wind-down is preparation time and is not counted as sleep duration.
- **中文**：一周追踪用用户自报记录统计，不代表设备验证过的真实睡眠。  
  **English**: Weekly tracking uses self-reported logs, not verified sleep measurements.
- **中文**：遇到严重失眠、疑似睡眠呼吸暂停、长期疲劳等情况，应寻求专业帮助。  
  **English**: Severe insomnia, suspected sleep apnea, or long-term fatigue should be handled with professional help.

---

# 中文说明

## 当前实现

当前仓库交付的是一个可移植 Agent Skill 和 CLI 工具：

- `r90_sleep_planner`：skill 提示词、回复规则和安全边界。
- `r90_calc.py`：确定性计算脚本，负责所有时间和周统计计算。
- 本地 JSON 睡眠记录，支持按日期 upsert，不重复记录同一天。
- OpenClaw、Codex、MiClaw 平台适配说明。
- `self-test` 内置验证。

目前还没有独立 Web 或移动 App；当前可用入口是 Agent Skill 和 CLI。

## 主要能力

- 输入“我明天9点起床”，展示 4/5/6 周期的睡觉窗口。
- 输入“我要睡了”，以当前时间为入睡参考，推荐 4/5/6 周期的起床时间。
- 默认 30 分钟 wind-down，且不计入睡眠时长。
- 支持跨天提示和 IANA 时区。
- 支持早晨低成本打卡：`23:30-07:00`、`11点半到7点`、`睡了7.5h`、`5`、`跳过`。
- 本地周统计：目标默认 35 个周期，最低参考范围默认 28-30 个周期。
- 保守健康文案，不做医疗承诺。

## 仓库结构

- `skills/r90-sleep-planner/SKILL.md`：通用 skill 指令和回复行为。
- `skills/r90-sleep-planner/scripts/r90_calc.py`：CLI 计算器和本地记录工具。
- `skills/r90-sleep-planner/references/data_contracts.md`：skill 数据契约。
- `skills/r90-sleep-planner/references/openclaw.md`：OpenClaw 安装、cron 和推送说明。
- `skills/r90-sleep-planner/references/codex.md`：Codex 安装、执行和自动化说明。
- `skills/r90-sleep-planner/references/miclaw.md`：MiClaw 兼容和工具契约说明。
- `DATA-CONTRACTS.md`、`USER-FLOWS.md`、`SAFEGUARDS.md`、`STATE.md`：产品级项目记忆。

## 环境要求

- Python 3.9 或更新版本。
- 不需要第三方 Python 包。
- 如果作为 skill 部署，宿主需要能读取 `SKILL.md`。
- 如果要使用确定性计算，宿主需要能执行 `python3 scripts/r90_calc.py`，或提供等价工具桥接。

## 平台支持

| 平台 | 状态 | 推荐用途 |
| --- | --- | --- |
| OpenClaw | 支持 workspace skills | 聊天 skill、cron 提醒、外部渠道推送 |
| Codex | 支持本地 skills | 本地 skill、CLI 验证、Codex 自动化 |
| MiClaw | 提供适配契约 | 注册为 skill/tool bundle，或暴露脚本为 host action |
| 纯 CLI | 完整支持 | 直接计算和本地 JSON 记录 |

## 获取和验证

```bash
git clone https://github.com/noodlebar/R90.git
cd R90
python3 skills/r90-sleep-planner/scripts/r90_calc.py self-test
```

预期结果：

```json
{
  "ok": true,
  "tests": ["windows", "wake", "weekly", "record", "checkin"]
}
```

## OpenClaw 部署

### Workspace 安装

OpenClaw 可以从 workspace 的 `skills/` 目录加载 skill。确保目录存在：

```text
<workspace>/skills/r90-sleep-planner/SKILL.md
```

如果 OpenClaw workspace 就是本仓库，不需要额外复制。

刷新并检查：

```bash
openclaw gateway restart
openclaw skills list
```

可测试：

```text
我明天9点起床
```

```text
我要睡了
```

### OpenClaw 早晨提醒

当前会话提醒：

```bash
openclaw cron add --name "R90 morning check-in" --cron "0 10 * * *" --tz "Asia/Shanghai" --session main --system-event "R90 morning check-in. Send exactly this concise prompt in Chinese: 早，记一下昨晚睡眠。大约几点睡、几点醒？直接回：23:30-07:00。不记就回：跳过. When the user replies, use r90_sleep_planner checkin parsing. Record parsed cycles for yesterday, then respond with the updated weekly total in one short sentence." --wake now
```

外部聊天推送需先确认渠道权限和目标 ID：

```bash
openclaw cron add --name "R90 morning check-in" --cron "0 10 * * *" --tz "Asia/Shanghai" --session isolated --message "Return only this plain-text message. Do not wrap it in JSON. Do not output a text field. Message: 早，记一下昨晚睡眠。大约几点睡、几点醒？直接回：23:30-07:00。不记就回：跳过" --announce --channel feishu --to "<verified-chat-target>"
```

如果推送显示成 `{"text":"..."}`，说明 cron message 需要改成纯文本输出。更多说明见 `skills/r90-sleep-planner/references/openclaw.md`。

## Codex 部署

复制 skill 到 Codex skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/r90-sleep-planner"
cp -R skills/r90-sleep-planner/. "${CODEX_HOME:-$HOME/.codex}/skills/r90-sleep-planner/"
```

验证部署副本：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/r90-sleep-planner/scripts/r90_calc.py" self-test
```

可测试：

```text
我明天 9 点起床，几点睡？
```

```text
我要睡了，帮我算几个适合的起床时间
```

```text
早，昨晚 23:30-07:00
```

如果 Codex 环境提供 automations/reminders，提醒文案应保持纯文本：

```text
早，记一下昨晚睡眠。
大约几点睡、几点醒？直接回：23:30-07:00
不记就回：跳过
```

用户回复后，再调用 `checkin` 记录对应睡眠日期。更多说明见 `skills/r90-sleep-planner/references/codex.md`。

## MiClaw 部署

MiClaw 是否能直接加载取决于宿主实现。R90 的最低要求是：

- 能读取 `SKILL.md`，或把内容注册为系统/工具指令。
- 能执行 `python3 scripts/r90_calc.py`，或暴露等价 host action。
- 可选：私有本地存储 `~/.r90/sleep-log.json`。
- 可选：宿主提醒/推送能力。

推荐工具契约：

```text
r90.windows(wakeTime, wakeDate, windDownMinutes=30, cycleOptions=[4,5,6], timezone)
r90.wake(now=true | sleepTime, sleepDate, cycleOptions=[4,5,6], timezone)
r90.checkin(reply, date=yesterday, store="~/.r90/sleep-log.json", timezone)
r90.weekly(weekStart, entriesFile | entriesJson, target=35)
```

用户可见回复应渲染为纯文本；原始 JSON 只用于调试或内部状态。更多说明见 `skills/r90-sleep-planner/references/miclaw.md`。

## CLI 直接使用

### 计算起床目标对应的睡觉窗口

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py windows \
  --wake-time 09:00 \
  --wake-date 2026-05-04 \
  --wind-down 30 \
  --cycles 4,5,6 \
  --timezone Asia/Shanghai
```

### “我要睡了”时计算起床时间

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py wake \
  --now \
  --cycles 4,5,6 \
  --timezone Asia/Shanghai
```

### 记录早晨打卡

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py checkin \
  --reply "23:30-07:00" \
  --date 2026-05-02 \
  --store ~/.r90/sleep-log.json \
  --timezone Asia/Shanghai
```

### 查看一周统计

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py weekly \
  --week-start 2026-04-27 \
  --entries-file ~/.r90/sleep-log.json \
  --target 35
```

## 数据存储

默认本地记录文件：

```text
~/.r90/sleep-log.json
```

示例记录：

```json
{
  "date": "2026-05-02",
  "actualCycles": 5,
  "plannedCycles": 6,
  "note": "optional note",
  "updatedAt": "2026-05-03T10:00:00+08:00"
}
```

本项目默认不上传睡眠日志。同一天重复记录会更新已有记录，不会创建重复条目。

## 行为规则

- `我明天9点起床` 这类快捷指令必须展示默认 4/5/6 周期。
- `我要睡了` 表示以当前时间为入睡参考，不能复用之前推荐的 bedtime。
- 早晨打卡只问大约入睡和起床时间，不要求用户自己计算 R90。
- 定时提醒输出应是纯文本。
- 严重失眠、疑似睡眠呼吸暂停、长期疲劳等情况应提示寻求专业帮助。

---

# English Guide

## Current Deliverable

R90 currently ships as a portable Agent Skill and deterministic CLI utility:

- `r90_sleep_planner`: skill instructions, response rules, and safety boundaries.
- `r90_calc.py`: deterministic calculator used for all arithmetic.
- Local JSON logging for self-reported sleep-cycle check-ins.
- Platform adapter notes for OpenClaw, Codex, and MiClaw.
- Built-in validation through `self-test`.

There is no standalone web or mobile app yet. The usable surfaces are the Agent Skill and the bundled CLI script.

## Features

- Bedtime windows from a wake target, showing 4, 5, and 6 cycles by default.
- Wake suggestions from a provided lights-out time or from "I am going to sleep now".
- Optional wind-down buffer, defaulting to 30 minutes, kept separate from sleep duration.
- Previous-day and next-day rollover notes.
- IANA timezone support through Python `zoneinfo`.
- Low-friction check-in parsing, such as `23:30-07:00`, `slept 7.5h`, `5`, or `skip`.
- Idempotent local sleep-log updates by date.
- Weekly R90 summary with target cycles, minimum useful range, and per-day rows.
- Conservative, non-clinical health language.

## Repository Layout

- `skills/r90-sleep-planner/SKILL.md`: portable skill instructions and response behavior.
- `skills/r90-sleep-planner/scripts/r90_calc.py`: CLI calculator and local log utility.
- `skills/r90-sleep-planner/references/data_contracts.md`: skill-level data contracts.
- `skills/r90-sleep-planner/references/openclaw.md`: OpenClaw installation, cron, and delivery notes.
- `skills/r90-sleep-planner/references/codex.md`: Codex placement, execution, and automation notes.
- `skills/r90-sleep-planner/references/miclaw.md`: MiClaw compatibility and tool-contract notes.

## Requirements

- Python 3.9 or newer.
- No third-party Python packages.
- An agent host that can read `SKILL.md`, if deploying as a skill.
- Shell access to run `python3 scripts/r90_calc.py`, or a host tool bridge that exposes the script commands.

## Platform Support

| Platform | Status | Best Use |
| --- | --- | --- |
| OpenClaw | Supported through workspace skills | Chat skill plus cron reminders and external channel delivery |
| Codex | Supported through local skills | Local skill execution, CLI validation, and Codex automations where available |
| MiClaw | Adapter contract provided | Register as a skill/tool bundle or expose script commands as host actions |
| Plain CLI | Fully supported | Direct deterministic calculations and local JSON logs |

## Get And Validate

```bash
git clone https://github.com/noodlebar/R90.git
cd R90
python3 skills/r90-sleep-planner/scripts/r90_calc.py self-test
```

Expected result:

```json
{
  "ok": true,
  "tests": ["windows", "wake", "weekly", "record", "checkin"]
}
```

## OpenClaw Deployment

OpenClaw can load workspace skills from:

```text
<workspace>/skills/r90-sleep-planner/SKILL.md
```

Refresh skill loading if needed:

```bash
openclaw gateway restart
openclaw skills list
```

Example prompts:

```text
I need to wake up at 9 tomorrow.
```

```text
I am going to sleep now.
```

Morning reminder, current session:

```bash
openclaw cron add --name "R90 morning check-in" --cron "0 10 * * *" --tz "Asia/Shanghai" --session main --system-event "R90 morning check-in. Send exactly this concise prompt in English: Morning check-in. What time did you roughly fall asleep and wake up? Reply like: 23:30-07:00. Reply skip to skip. When the user replies, use r90_sleep_planner checkin parsing. Record parsed cycles for yesterday, then respond with the updated weekly total in one short sentence." --wake now
```

More OpenClaw notes are in `skills/r90-sleep-planner/references/openclaw.md`.

## Codex Deployment

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/r90-sleep-planner"
cp -R skills/r90-sleep-planner/. "${CODEX_HOME:-$HOME/.codex}/skills/r90-sleep-planner/"
python3 "${CODEX_HOME:-$HOME/.codex}/skills/r90-sleep-planner/scripts/r90_calc.py" self-test
```

Example prompts:

```text
I need to wake up at 9 tomorrow. What are my sleep windows?
```

```text
I am going to sleep now. What are good wake times?
```

If Codex provides automations/reminders, use plain text:

```text
Morning check-in.
What time did you roughly fall asleep and wake up?
Reply like: 23:30-07:00
Reply skip to skip.
```

More Codex notes are in `skills/r90-sleep-planner/references/codex.md`.

## MiClaw Deployment

MiClaw compatibility depends on host support. R90 requires:

- ability to read `SKILL.md`, or register it as host instructions.
- ability to execute `python3 scripts/r90_calc.py`, or expose equivalent host actions.
- optional local/private storage for `~/.r90/sleep-log.json`.
- optional host reminder delivery.

Recommended tool contract:

```text
r90.windows(wakeTime, wakeDate, windDownMinutes=30, cycleOptions=[4,5,6], timezone)
r90.wake(now=true | sleepTime, sleepDate, cycleOptions=[4,5,6], timezone)
r90.checkin(reply, date=yesterday, store="~/.r90/sleep-log.json", timezone)
r90.weekly(weekStart, entriesFile | entriesJson, target=35)
```

Render user-facing responses as plain text. Keep raw JSON for debugging or internal host state. More MiClaw notes are in `skills/r90-sleep-planner/references/miclaw.md`.

## CLI Usage

Calculate bedtime windows:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py windows \
  --wake-time 09:00 \
  --wake-date 2026-05-04 \
  --wind-down 30 \
  --cycles 4,5,6 \
  --timezone Asia/Shanghai
```

Calculate wake suggestions from now:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py wake \
  --now \
  --cycles 4,5,6 \
  --timezone Asia/Shanghai
```

Record a check-in:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py checkin \
  --reply "23:30-07:00" \
  --date 2026-05-02 \
  --store ~/.r90/sleep-log.json \
  --timezone Asia/Shanghai
```

Summarize a week:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py weekly \
  --week-start 2026-04-27 \
  --entries-file ~/.r90/sleep-log.json \
  --target 35
```

## Data Storage

Default local log file:

```text
~/.r90/sleep-log.json
```

Records are local by default and are upserted by `date`.

## Behavior Notes

- Wake-target shortcuts must show all default 4/5/6 cycle options.
- "I am going to sleep now" means the current time is the lights-out reference.
- Morning check-ins should ask for approximate sleep and wake times, not ask the user to calculate cycles manually.
- Scheduled reminder output should be plain text.
- Severe insomnia, suspected sleep apnea, long-term fatigue, or other health-risk contexts should be handled conservatively and directed toward professional help.

## Project Memory

This repository follows a Portfolio OS operating model:

- `STATE.md`: current stage, risks, and next step.
- `SAFEGUARDS.md`: safety boundaries and validation baseline.
- `DECISIONS.md`: key project decisions.
- `WORKFLOWS.md`: reusable workflows.
- `codex/MODES.md`: `Explore`, `Build`, and `Release` definitions.
- `DATA-CONTRACTS.md`: product-level data contracts.
- `USER-FLOWS.md`: calculator user flows.
- `AGENTS.md`: multi-agent roles and write boundaries.

## License

R90 is released under the MIT License. See `LICENSE` for details.
