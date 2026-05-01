# State

## Current stage
discovery

## Working now

- define the first local calculator milestone
- capture the R90 cycle assumptions and safety boundaries
- initialize local git history for the project

## Risks

- R90 is wellness planning guidance, not medical advice
- users may interpret cycle math as a promise of sleep quality
- time calculations can be wrong around date rollover, DST, and timezone changes
- scope can drift into habit coaching before the calculator is useful

## Open questions

- preferred stack: lightweight web app, CLI, or mobile-first PWA
- whether to support weekly history in v1 or keep it as derived-only output
- whether the UI language should start in Chinese, English, or bilingual

## Next milestone

Build a local MVP that calculates bedtime windows from a target wake time using 90-minute cycles, with options for 4, 5, and 6 cycles plus an optional wind-down buffer.
