# R90

R90 is a Codex skill and deterministic CLI utility for planning sleep around 90-minute recovery cycles. It calculates bedtime windows from a target wake time, suggests wake times from a lights-out time, and records lightweight weekly R90 cycle logs.

This project is wellness planning guidance, not medical advice. It does not diagnose sleep problems, treat medical conditions, or guarantee sleep quality.

## What Is Implemented

The current repository ships a working Codex skill:

- `r90_sleep_planner`: the skill prompt, response rules, and safety boundaries.
- `r90_calc.py`: the deterministic calculator used by the skill for all arithmetic.
- Local JSON logging for self-reported sleep-cycle check-ins.
- Built-in validation through `self-test`.

There is not yet a standalone web or mobile app. The first usable surface is the Codex skill plus the bundled CLI script.

## Main Features

- Bedtime windows from a wake target, using 4, 5, and 6 cycles by default.
- Wake suggestions from a planned lights-out time, including "I am going to sleep now" flows.
- Optional wind-down buffer, defaulting to 30 minutes, kept separate from sleep duration.
- Explicit previous-day and next-day rollover notes.
- IANA timezone support through Python `zoneinfo`.
- Daily check-in parsing from low-friction replies such as `23:30-07:00`, `睡了7.5h`, `5`, or `跳过`.
- Idempotent local sleep-log updates by date.
- Weekly R90 summary with target cycles, minimum useful range, and per-day rows.
- Conservative health language and non-clinical disclaimers.

## Repository Layout

- `skills/r90-sleep-planner/SKILL.md`: Codex skill instructions and response behavior.
- `skills/r90-sleep-planner/scripts/r90_calc.py`: CLI calculator and local log utility.
- `skills/r90-sleep-planner/references/data_contracts.md`: exact skill-level data contracts.
- `DATA-CONTRACTS.md`: product-level input, output, and validation contracts.
- `USER-FLOWS.md`: first calculator flows and edge cases.
- `SAFEGUARDS.md`: health, data, and release boundaries.
- `STATE.md`: current project stage, risks, and next milestone.
- `DECISIONS.md`: project decisions and tradeoffs.
- `WORKFLOWS.md`: repeatable implementation workflow.
- `codex/MODES.md`: Explore, Build, and Release mode definitions.

## Requirements

- Python 3.9 or newer.
- No third-party Python packages are required.
- A Codex environment that supports local skills, if you want to deploy it as a skill.

## Deploy As A Codex Skill

Clone the repository:

```bash
git clone https://github.com/noodlebar/R90.git
cd R90
```

Install the skill into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/r90-sleep-planner"
cp -R skills/r90-sleep-planner/. "${CODEX_HOME:-$HOME/.codex}/skills/r90-sleep-planner/"
```

Validate the deployed copy:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/r90-sleep-planner/scripts/r90_calc.py" self-test
```

Expected result:

```json
{
  "ok": true,
  "tests": ["windows", "wake", "weekly", "record", "checkin"]
}
```

After installation, ask Codex questions such as:

```text
我明天 9 点起床，几点睡？
```

```text
我要睡了，帮我算几个适合的起床时间
```

```text
早，昨晚 23:30-07:00
```

The skill is designed to answer in the user's language. Chinese prompts receive concise Chinese sleep-window summaries.

## Use The CLI Directly

You can run the calculator from the repository without installing the skill:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py self-test
```

### Calculate Bedtime Windows

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py windows \
  --wake-time 07:00 \
  --wake-date 2026-05-04 \
  --wind-down 30 \
  --cycles 4,5,6 \
  --timezone Asia/Shanghai
```

This returns JSON with:

- `inBedAt`: when wind-down should begin.
- `lightsOutAt`: the planned start of sleep.
- `wakeAt`: the target wake datetime.
- `cycleCount` and `sleepMinutes`.
- rollover or timezone offset notes when relevant.

### Calculate Wake Suggestions

From a provided lights-out time:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py wake \
  --sleep-time 23:30 \
  --sleep-date 2026-05-03 \
  --cycles 4,5,6 \
  --timezone Asia/Shanghai
```

From the current local time:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py wake \
  --now \
  --cycles 4,5,6 \
  --timezone Asia/Shanghai
```

### Record A Daily Check-In

Record a known cycle count:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py record \
  --date 2026-05-02 \
  --actual-cycles 5 \
  --planned-cycles 6 \
  --store ~/.r90/sleep-log.json \
  --timezone Asia/Shanghai
```

Parse an easy morning reply and record it:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py checkin \
  --reply "23:30-07:00" \
  --date 2026-05-02 \
  --store ~/.r90/sleep-log.json \
  --timezone Asia/Shanghai
```

Accepted check-in replies include:

- `23:30-07:00`
- `11点半到7点`
- `睡了7.5h`
- `5`
- `跳过`

Daily records are upserts by `date`, so repeating the same check-in date updates the existing record instead of creating duplicates.

### Summarize A Week

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py weekly \
  --week-start 2026-04-27 \
  --entries-file ~/.r90/sleep-log.json \
  --target 35
```

The weekly summary reports:

- actual completed cycles.
- planned cycles where available.
- target cycles, defaulting to 35.
- cycles remaining to target.
- minimum useful range, defaulting to 28-30 cycles.
- seven daily rows.

## Data Storage

The CLI stores self-reported logs as a local JSON array when `--store` is used. The default store for skill-oriented usage is:

```text
~/.r90/sleep-log.json
```

Records look like:

```json
{
  "date": "2026-05-02",
  "actualCycles": 5,
  "plannedCycles": 6,
  "note": "optional note",
  "updatedAt": "2026-05-03T10:00:00+08:00"
}
```

The project does not upload sleep logs by default.

## Skill Behavior Notes

- Wake-target shortcuts such as `我明天9点起床` must show all default 4, 5, and 6 cycle options.
- `我要睡了` means the current time is the lights-out reference. The skill must not reuse an earlier bedtime recommendation.
- Morning check-ins should ask for approximate sleep and wake times, not ask the user to calculate cycles manually.
- Reminder output should be plain text when used in scheduled chat jobs.
- Severe insomnia, suspected sleep apnea, long-term fatigue, or other health-risk contexts should be handled conservatively and directed toward professional help.

## Local Validation

Run:

```bash
python3 skills/r90-sleep-planner/scripts/r90_calc.py self-test
```

The self-test covers:

- bedtime windows.
- wake suggestions.
- weekly summary.
- daily record upserts.
- check-in parsing.

## Project Status

The implemented deliverable is the R90 Codex skill and CLI calculator. The next product milestone is a local MVP calculator screen built around the tested calculation function.

Open decisions are tracked in `STATE.md`, including implementation stack, UI language, and whether weekly history belongs in v1.

## Codex Project Memory

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
