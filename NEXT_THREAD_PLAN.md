# Next Thread Plan

## North Star

Take the companion from "smart custom toy" to "trustworthy desktop instrument":

- tiny
- transparent
- calm
- truthful
- pleasant to touch

If there is a tradeoff between extra features and better truthfulness, choose truthfulness.

## What The Project Is Becoming

Not a desktop pet.
Not a widget panel.
Not a Codex dashboard.

It should feel like a quiet field unit that appears present when real agent work is happening, fades into the background when it is not, and never lies casually.

## Current Position

The project already has:

- transparent topmost pod presentation
- shaped click-through hit testing
- right-click menu, drag, and redock
- pause/resume as a hard resync
- persistent position/debug state
- a diagnostics window
- a richer phase model than the original idle/working split
- a confidence-gated state model instead of blunt branch-only sensing
- a rolling sensor trace in diagnostics showing chosen/candidate state and rejected reasons
- quieter display handling for ambiguous `thinking` and `waiting` reads
- a lightweight reasoning probe that tails the active Codex rollout jsonl for live `response_item` reasoning events
- reasoning hit or miss visibility in diagnostics with age and trace context
- read-only live validation showing real rollout reasoning hits arrive before assistant messages and then clear back to `rollout already answered`
- read-only live validation showing a real child `python.exe` tool path still chooses `tooling` and rejects `thinking` with `child path present`

The biggest remaining weakness is no longer "find a source." It is to prove and tune the new reasoning probe against real live Codex app cases so `thinking` feels honest and non-sticky.

## Thread Status Snapshot

- repo is currently dirty by design:
  - `NEXT_THREAD_PLAN.md`
  - `README.md`
  - `codex_ascii_companion.pyw`
- current head:
  - `80851bd`
- compile check passed after the reasoning-probe change:
  - `python -m py_compile C:\Users\raymo_w9whwcn\OneDrive\TT\codex_ascii_companion\codex_ascii_companion.pyw`
- implementation checks already showed:
  - shell-only descendants stay `idle`
  - 2-poll root pulses stay `idle`
  - 3-poll root pulses can earn `thinking`
  - active build-like descendants become `building`
  - quiet descendants after prior real work can become `waiting`
  - the reasoning probe finds live rollout `response_item` reasoning events from the active `.codex\sessions` jsonl
- relaunch check passed after the change:
  - `powershell -ExecutionPolicy Bypass -File C:\Users\raymo_w9whwcn\OneDrive\TT\codex_ascii_companion\relaunch_companion.ps1`
- live validation update on 2026-04-20:
  - the most recent observed reasoning-to-assistant gap was about `1.5s`, which still fits inside the current `550 ms` poll plus `0.9 s` reasoning-probe cadence
  - the probe now reports `rollout already answered` after the assistant message lands, which is the intended clear behavior
  - no timing-window code changes were needed from terminal-side validation alone
- live Tk-window validation update on 2026-04-20:
  - diagnostics showed a real `idle -> thinking` transition from `rollout reasoning hit 0.6s ago`
  - the pod then cleared back through `thinking -> delivered`, which matches the intended post-answer behavior
  - a live child tool path still forced `tooling` and showed `thinking held: child path present`
  - the first GUI-facing pass did not require timing-window changes
- optimization pass update on 2026-04-20:
  - the process snapshot PowerShell command is now reused instead of rebuilt every poll
  - the rollout reasoning probe now incrementally parses only newly appended jsonl lines and only briefly reuses the last rollout path before rescanning
  - diagnostics summary/log rendering is lazy while the diagnostics window is hidden
  - repeated display layout and hit-shape geometry are cached per frame and quote combination
  - polling now backs off slightly when no live `codex.exe app-server` is present
  - compile and relaunch both passed after the optimization pass without any sensing-threshold changes

## Next Milestone

### Theme

Misfire watch, then native-feel pass.

### Goal

Keep `thinking` honest under real use, then simplify the display once that honesty feels stable.

## Priority Order

1. Diagnostics capture for false positives and false negatives
2. Timing-window tuning only if a live miss or sticky read appears
3. Visual simplification around trusted states
4. Packaging and launch polish

## Thread 1 Mission

Improve sensing until these are true:

- `thinking` is rare, earned, and tied to a real reasoning signal when possible
- `tooling` means a real child tool path is active
- `building` means something build-like is actually underway
- `waiting` means work still exists but has gone quiet
- `delivered` feels like a short, satisfying handoff instead of random animation
- `idle` is the default when signals are weak or ambiguous

## Concrete Work For The Next Thread

### 1. Stay In Validation Mode, But Only For Real Misfires

- The first live diagnostics pass already confirmed:
  - a real rollout reasoning hit can drive `thinking`
  - the pod clears back out after the assistant answer
  - child-path work still suppresses `thinking`
- Do not keep re-running the same happy path unless something now feels wrong.
- Look for the next useful capture:
  - a sticky `thinking` read
  - a missed reasoning hit
  - a false `thinking` during real child-path work
  - a missed or delayed rollout pickup right after switching to a different active Codex thread
  - an awkwardly slow pickup after cold-starting Codex from a no-app-server idle state

### 2. Tune Only If The Live Read Demands It

- Adjust the tail window or hold timing only if the probe is sticky or misses real thinking.
- Keep the check trigger-style and light.
- If the probe proves brittle, degrade gracefully to the existing confidence gate instead of adding heavier plumbing.

### 3. Use Misfire Capture, Do Not Rebuild It

- Use the rolling sensor trace in diagnostics.
- Capture the last several polls with:
  - chosen state
  - candidate state
  - root cpu delta
  - reasoning hit or miss and age
  - descendant counts
  - winning process or hint
  - why a state was rejected
- Make it possible to inspect a false state quickly without attaching a full logger forever.

### 4. Refine The Display Contract

- Re-evaluate whether every state needs text.
- Keep the visible language stronger than the prose.
- Prefer a slightly better animation or read over adding more words.
- If a state is ambiguous, reduce visual intensity instead of inventing certainty.

### 5. Decide Whether Tk Has Reached Its Ceiling

Do not migrate just because native would be "cooler."
Do consider a move off Tk if it clearly unlocks one or more of these:

- cleaner transparent rendering
- better hit testing or input behavior
- more reliable shaped interaction
- smoother tiny animations
- simpler packaging

If Tk is still good enough after the truth pass, keep it.

### 6. Package Only After Trust Improves

- Add a repeatable build path for a single-file Windows executable.
- Add shortcut or icon refresh helpers only if they stay tiny.
- Do not do packaging before the sensing model feels honest.

## Acceptance Criteria For The Next Thread

The next thread should aim to leave the repo with all of these true:

- the pod no longer casually drifts into `thinking`
- at least one real app-side `thinking` case was observed and used to tune the signal
- at least one real false-positive case was observed and tuned against
- diagnostics make state choice legible in plain English
- the visible states feel cleaner, not busier
- the repo stays clean and runnable with a single restart command

## Taste Guardrails

- no panels
- no bars
- no mascot sprawl
- no generic neon cyberpunk clutter
- no fake emotional overacting
- no fantasy states that are not backed by signals

The emotional target remains:

- present
- capable
- calm
- responsive

## Starting Point Commands

```powershell
python -m py_compile C:\Users\raymo_w9whwcn\OneDrive\TT\codex_ascii_companion\codex_ascii_companion.pyw
```

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\raymo_w9whwcn\OneDrive\TT\codex_ascii_companion\relaunch_companion.ps1
```

## First Move I Want In The New Thread

Keep diagnostics available and wait for a naturally occurring misfire or awkward read. If none appears quickly, move to display-contract cleanup instead of reworking the sensing model again.
