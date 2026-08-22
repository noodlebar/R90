# User Flows

## Flow 1: Early Meeting

Trigger:

```text
我明天 8 点起。
```

Behavior:

- Interpret as a wake-target bedtime-window request.
- Use tomorrow's local date.
- Return 6/5/4-cycle options.
- Treat `熄灯` as the actual sleep target and `上床` as wind-down start.

Acceptance example:

```text
明天 08:00 起床的话：

6 周期：23:00 熄灯（9小时）
5 周期：00:30 熄灯（7.5小时）
4 周期：02:00 熄灯（6小时）

如果提前放松 30 分钟，上床时间分别是 22:30 / 00:00 / 01:30。
```

## Flow 2: Sleep Now

Trigger:

```text
我现在要睡了。
```

Behavior:

- Use current local time as `lightsOutAt`.
- Return wake options for 4/5/6 cycles.
- Mention that this is not a system alarm unless the host can create alarms.
- Never reuse a previous bedtime-window answer as the current lights-out time.

Acceptance:

- The response includes the actual reference time.
- The response includes three wake options.
- The response stays concise and in the user's language.

## Flow 3: Daily Check-in

Trigger:

```text
早，记一下昨晚睡眠。
直接回周期数：5
记不清就回时间段：23:30-07:00
不记回：跳过
```

Behavior:

- Host automation sends the prompt as plain text.
- User replies with a cycle count, time range, duration, or skip.
- Skill records the previous local sleep date.
- Same-date replies update existing records.
- Weekly KPI is recalculated after a saved entry.

Acceptance:

- `5` records 5 full cycles.
- `23:30-07:00` records 5 full cycles.
- `11点半到7点` records 5 full cycles.
- `跳过` reports a skipped check-in without affecting cycle totals.
- Duplicate replies for the same reminder do not create duplicate rows.

## Edge Cases

- Missing wake time: ask only for the wake time.
- Ambiguous `9点`: use context; `明天9点起` means `09:00` wake time.
- Bedtime or wake time crosses midnight: preserve the correct local date.
- DST or timezone transitions: use elapsed-time arithmetic and expose offset-change notes.
- Severe insomnia or health-risk language: respond conservatively and recommend professional help.
- No persistent storage: calculate or parse, but do not claim the log was saved.
