# Decisions

## R90 - Use this repository as the single source of truth

Context:
R90 previously had a published repository and a separate unversioned `r90-agent-skill` working copy.

Decision:
Use the `R90` repository as the only maintained source project. Merge reusable skill, adapter, contract, and workflow improvements into this repository instead of maintaining a second project tree.

Why:
One Git history and one set of canonical files prevent deployment drift and unclear ownership.

Tradeoffs:
Installed host copies still require an explicit sync step after repository changes.

## R90 - Keep the utility focused

Context:
R90 is a practical planning utility with clear inputs, outputs, and validation rules.

Decision:
Keep the deliverable centered on a portable Agent Skill, deterministic CLI, local logging, and thin host adapters.

Why:
This preserves portability and keeps calculation behavior testable.

Tradeoffs:
R90 is not a full sleep-coaching product, wearable integration, or medical workflow.

## R90 - Anchor calculations on wake time

Context:
Nick Littlehales' R90 framing uses 90-minute cycles and emphasizes planning around a consistent wake anchor.

Decision:
The wake-target flow calculates backwards from the target wake time. The going-to-sleep flow calculates forwards from the actual current local time.

Why:
These flows match the user's real moments: "I need to wake at X" and "I am going to sleep now."

Tradeoffs:
The utility does not personalize cycle length or infer actual sleep onset latency.

## R90 - Treat health guidance conservatively

Context:
Sleep planning sits near health and wellbeing, and users may over-trust calculator output.

Decision:
Keep language in the planning-guidance lane, include a short non-clinical disclaimer, and avoid claims that a specific window guarantees recovery.

Why:
This protects users and keeps the project scope honest.

Tradeoffs:
The copy may feel less motivational than wellness apps that make stronger promises.

## R90 - Keep scheduling host-owned

Context:
Codex, OpenClaw, MiClaw, and SLI differ in notification, cron, native alarm, and storage capabilities.

Decision:
Keep calculation and response rules in the skill. Keep scheduling, delivery, alarm permissions, external credentials, and host-private storage in adapter layers.

Why:
This keeps the core skill portable and prevents claims that a chat skill created a real alarm.

Tradeoffs:
Each host needs a small adapter or setup step for daily check-ins.
