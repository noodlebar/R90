# User Flows

## Main flows

### First-run setup

1. User opens the calculator.
2. App asks for target wake time.
3. App defaults to 4, 5, and 6 cycle options with a 30-minute wind-down buffer.
4. App shows calculated in-bed and lights-out windows.

### Primary happy path

1. User enters a wake time, for example `07:00`.
2. User keeps default options.
3. App returns bedtime windows, sorted from more sleep to less sleep.
4. User picks one window and can copy or save it.

### Review or correction path

1. User changes wind-down duration or cycle options.
2. App recalculates immediately.
3. App highlights previous-day bedtime rollover when relevant.
4. App updates weekly cycle impact if weekly planning is enabled.

## Edge cases

- invalid or missing wake time
- wake time close to current time
- bedtime rolls into the previous day
- daylight saving time transition
- user selects fewer than 3 cycles or more than 7 cycles
- weekly total below the target range
