# OpenClaw Adapter

Use this reference only when installing, scheduling, or troubleshooting R90 inside OpenClaw.

## Placement

OpenClaw uses R90 as a single `SKILL.md` file. Paste or upload this file into the OpenClaw skill configuration:

```text
skills/r90-sleep-planner/SKILL.md
```

The skill should still prefer `python3 scripts/r90_calc.py` when a shell/tool bridge can reach it. For OpenClaw, deploy only `SKILL.md`; when scripts are unavailable, use the manual algorithms in `SKILL.md`.

For an OpenClaw setup with shell access, place the script at a stable path such as:

```text
~/openclaw-tools/r90_calc.py
```

Then replace script examples in `SKILL.md` with the absolute command path:

```bash
python3 ~/openclaw-tools/r90_calc.py wake --now --cycles 4,5,6 --timezone Asia/Shanghai
python3 ~/openclaw-tools/r90_calc.py checkin --reply "23:30-07:00" --date 2026-05-02 --store ~/.r90/sleep-log.json --timezone Asia/Shanghai
```

## Scheduling

The skill does not schedule itself. Use OpenClaw cron for morning check-ins.

In-app/current-session reminder:

```bash
openclaw cron add --name "R90 morning check-in" --cron "0 10 * * *" --tz "Asia/Shanghai" --session main --system-event "R90 morning check-in. Send exactly this concise prompt in Chinese: 早，记一下昨晚睡眠。大约几点睡、几点醒？直接回：23:30-07:00。不记就回：跳过. When the user replies, use r90_sleep_planner checkin parsing. Record parsed cycles for yesterday, then respond with the updated weekly total in one short sentence." --wake now
```

External chat push after channel permissions are verified:

```bash
openclaw cron add --name "R90 morning check-in" --cron "0 10 * * *" --tz "Asia/Shanghai" --session isolated --message "Return only this plain-text message. Do not wrap it in JSON. Do not output a text field. Message: 早，记一下昨晚睡眠。大约几点睡、几点醒？直接回：23:30-07:00。不记就回：跳过" --announce --channel feishu --to "<verified-chat-target>"
```

## Delivery Rules

- `--session main --system-event` wakes the main session. It is good for an in-app/current-session reminder, but it is not a reliable external chat push.
- To push into Feishu/Slack/Telegram/etc., use isolated cron delivery with `--announce --channel ... --to ...` and valid channel credentials.
- If OpenClaw reports `unauthorized` or `Forbidden`, the issue is channel auth/target configuration, not this skill. This skill cannot grant chat-channel permissions.
- For cron-owned isolated jobs, do not ask the agent to use a separate message tool as a fallback; OpenClaw's cron runner owns final delivery.
- The isolated job's final answer must be plain text. Do not return a message object like `{"text":"..."}` because announce delivery may send that object literally.

If an existing reminder is sending `{"text":"..."}`, inspect and edit that cron job:

```bash
openclaw cron list
openclaw cron edit <job-id> --message "Return only this plain-text message. Do not wrap it in JSON. Do not output a text field. Message: 早，记一下昨晚睡眠。大约几点睡、几点醒？直接回：23:30-07:00。不记就回：跳过"
openclaw cron run <job-id>
```
