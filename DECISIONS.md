# Decisions

## R90 - Treat this as an independent project
Context:
This project is tracked as its own repo or folder inside the wider Portfolio OS.

Decision:
Keep this project isolated from unrelated repos and use repo-level operating docs.

Why:
Independent boundaries reduce context bleed and make Codex handoff more stable.

Tradeoffs:
Some shared logic may be duplicated until a second real reuse case appears.

## R90 - Start with the utility apps operating model
Context:
This project was bootstrapped with the `utility apps` template family.

Decision:
Use the default safeguards, modes, and domain docs first, then refine after real usage.

Why:
The initial goal is consistency and safety, not perfect abstraction.

Tradeoffs:
Some sections will stay placeholder-level until the first real milestone is built.

## R90 - Anchor calculations on wake time
Context:
The R90 method frames sleep planning around 90-minute cycles and a consistent wake anchor.

Decision:
The first calculator will ask for the user's target wake time, then count backwards in 90-minute blocks to generate bedtime windows.

Why:
This makes the tool immediately useful and keeps the first release focused on calculation rather than broad sleep coaching.

Tradeoffs:
The app will not initially personalize cycle length or infer sleep quality from wearable data.

## R90 - Treat health guidance conservatively
Context:
Sleep planning sits near health and wellbeing, and users may over-trust calculator output.

Decision:
Keep v1 language in the planning-guidance lane, include a short non-clinical disclaimer, and avoid claims that a specific window guarantees recovery.

Why:
This protects users and keeps the project scope honest.

Tradeoffs:
The copy may feel less motivational than wellness apps that make stronger promises.
