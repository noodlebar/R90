# Storyboard

**Format:** 1920x1080
**Duration:** 20.00 seconds
**Audio:** voiceover plus minimal electronic underscore, if available
**VO direction:** calm, precise, technically literate; leave small pauses after each sentence
**Style basis:** `DESIGN.md` using captured GitHub colors, Mona Sans VF, code panels, and repo screenshots

## Asset Audit

| Asset | Type | Assign to Beat | Role |
| --- | --- | --- | --- |
| `capture/screenshots/scroll-000.png` | Screenshot | Beat 1, Beat 5 | Repository/product proof, opener and closer |
| `capture/screenshots/scroll-025.png` | Screenshot | Beat 4 | Validation and deployment proof |
| `capture/screenshots/scroll-050.png` | Screenshot | Beat 5 | Weekly check-in and local JSON proof |
| `capture/assets/glow-1.png` | Image | Beats 1-5 | Soft night/recovery bloom |
| `capture/assets/favicon.png` | Image | Beat 5 | Small GitHub source marker |

## Beat 1: No More Guesswork (0.00-3.80s)

**VO cue:** "Sleep planning shouldn't be guesswork."

**Concept:** The viewer starts inside a dark repo-like workspace at night. A captured GitHub screenshot drifts behind a large R90 title while a precise blue cycle line begins to draw, replacing vague sleep intention with structure.

**Visual:** Full dark canvas, soft glow behind the title, screenshot framed as a tilted repo window on the right, large `R90` title on the left, and three small time chips forming a clean rhythm. Techniques: CSS 3D panel, SVG path drawing, per-word kinetic typography.

**Transition:** Velocity-matched upward into Beat 2.

## Beat 2: Wake Time Is The Anchor (3.80-7.80s)

**VO cue:** "R90 turns a wake time into practical 90-minute sleep windows, with wind-down kept separate."

**Concept:** A wake target locks into place, and the sleep windows calculate backwards in visible 90-minute blocks. The scene feels like a deterministic calculator, not a mood board.

**Visual:** Central circular wake anchor at `07:00`, six arc segments, three output rows for 6, 5, and 4 cycles, and a separate 30-minute wind-down bracket. Techniques: counter/timeline fill, SVG arc drawing, code-style output cards.

**Transition:** Blur-through to Beat 3.

## Beat 3: Going To Sleep Now (7.80-11.30s)

**VO cue:** "When you're going to sleep now, it suggests clean wake options."

**Concept:** The direction reverses: instead of planning backwards from morning, the present moment becomes the start. Options fan forward cleanly, like a terminal command resolving into choices.

**Visual:** Terminal card types `r90_calc.py wake --now`, then three wake options cascade onto the right. A slim animated cursor, blue connector lines, and a quiet glow imply nighttime use. Techniques: typing effect, cascading cards, animated connector path.

**Transition:** Hard cut on the command result.

## Beat 4: Deterministic Skill And CLI (11.30-15.50s)

**VO cue:** "As a Codex skill or CLI, it's deterministic, local, and easy to verify."

**Concept:** The product's trust moment. Captured README validation and a JSON pass panel show that R90 is portable, local, and testable.

**Visual:** Three platform chips lock in: Codex skill, pure CLI, local JSON. A screenshot panel scrolls subtly in the background while the foreground JSON block shows `"ok": true`. Techniques: screenshot Ken Burns, JSON highlight, chip cascade.

**Transition:** Whip pan left into Beat 5.

## Beat 5: Weekly Rhythm (15.50-20.00s)

**VO cue:** "Then morning check-ins turn nights into a lightweight weekly cycle log. R90. Plan the night. Wake with a cleaner target."

**Concept:** The video resolves from single-night planning into an ongoing weekly rhythm. The final frame is honest and calm: planning guidance, not medical advice.

**Visual:** Seven small day bars fill to cycle counts, a weekly total reaches `35`, and the repo screenshot returns as proof behind the CTA. Final lockup: `R90` plus `Plan the night. Wake with a cleaner target.` Techniques: bar animation, numeric counter, soft logo lockup.

**Transition:** End on held lockup.

## Production Architecture

```text
videos/r90-product-promo/
├── index.html
├── DESIGN.md
├── SCRIPT.md
├── STORYBOARD.md
├── narration.txt
├── capture/
│   ├── screenshots/
│   ├── assets/
│   └── extracted/
└── compositions/
```
