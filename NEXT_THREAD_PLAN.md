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

The biggest remaining weakness is still sensor truth. The pod can look good and still feel wrong if it claims thinking when nothing meaningful is happening.

## Next Milestone

### Theme

Truth pass, then native-feel pass.

### Goal

Make the state model feel reliable enough that the pod can be trusted in the corner of the eye.

## Priority Order

1. Sensor truth hardening
2. Diagnostics capture for false positives and false negatives
3. Visual simplification around trusted states
4. Packaging and launch polish

## Thread 1 Mission

Improve sensing until these are true:

- `thinking` is rare and earned
- `tooling` means a real child tool path is active
- `building` means something build-like is actually underway
- `waiting` means work still exists but has gone quiet
- `delivered` feels like a short, satisfying handoff instead of random animation
- `idle` is the default when signals are weak or ambiguous

## Concrete Work For The Next Thread

### 1. Harden The Evidence Model

- Replace the last bits of single-signal state decisions with a small evidence score or confidence gate.
- Separate "root activity exists" from "root activity is meaningful."
- Distinguish these signal classes explicitly:
  - descendant process birth/death
  - descendant CPU delta
  - build-like command hints
  - shell-only presence without activity
  - app-server-only pulses
- Bias ambiguous cases toward `idle`, not `thinking`.

### 2. Add Misfire Capture

- Add a tiny rolling sensor trace in diagnostics.
- Include the last several polls with:
  - chosen state
  - candidate state
  - root cpu delta
  - descendant counts
  - winning process/hint
  - why a state was rejected
- Make it possible to inspect a false state quickly without attaching a full logger forever.

### 3. Refine The Display Contract

- Re-evaluate whether every state needs text.
- Keep the visible language stronger than the prose.
- Prefer a slightly better animation/read over adding more words.
- If a state is ambiguous, reduce visual intensity instead of inventing certainty.

### 4. Decide Whether Tk Has Reached Its Ceiling

Do not migrate just because native would be "cooler."
Do consider a move off Tk if it clearly unlocks one or more of these:

- cleaner transparent rendering
- better hit testing/input behavior
- more reliable shaped interaction
- smoother tiny animations
- simpler packaging

If Tk is still good enough after the truth pass, keep it.

### 5. Package Only After Trust Improves

- Add a repeatable build path for a single-file Windows executable.
- Add shortcut/icon refresh helpers only if they stay tiny.
- Do not do packaging before the sensing model feels honest.

## Acceptance Criteria For The Next Thread

The next thread should aim to leave the repo with all of these true:

- the pod no longer casually drifts into `thinking`
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

Open diagnostics, intentionally reproduce at least one bogus `thinking` read, and redesign the state gate around that evidence instead of tuning blindly.
