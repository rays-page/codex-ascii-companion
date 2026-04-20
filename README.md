# Codex ASCII Companion

Small transparent Windows desktop companion for Codex.

It stays out of the way, lives near the clock, and reacts to real `codex.exe app-server` work instead of merely noticing that the Codex app is open.

## Files

- `codex_ascii_companion.pyw`: standalone companion app
- `codex_courier_pod.ico`: generated icon used by the window and shortcut
- `relaunch_companion.ps1`: clean stop/start helper for the running companion
- `companion_settings.json`: local position/debug settings file written at runtime and ignored by git

## Run

Use the Desktop shortcut, or run:

```powershell
pythonw .\codex_ascii_companion.pyw
```

For diagnostics on launch:

```powershell
pythonw .\codex_ascii_companion.pyw --debug
```

For a clean restart:

```powershell
.\relaunch_companion.ps1
```

## Behavior

- Left click: brief acknowledgement animation
- Double click: redock above the clock
- Right click: menu toggle, text toggle, redock, pause/resume sensing, diagnostics toggle, quit
- Pause/resume: clears stale snapshots and forces a fresh resync against the current Codex process tree
- Position: remembers the last dragged location and whether the pod was docked
- Theme sync: shadow treatment and window surfaces follow the Windows app light/dark theme instead of using one fixed drop shadow everywhere
- Text toggle: lets you hide the pod caption entirely if you want the character to stay visual-only

## Desktop Buddy

The attached menu stays visually tied to the pod instead of becoming a dashboard.

- `Clean files`: opens a Codex thread aimed at `Homebase` with a conservative file-organization prompt
- `Safety scan`: requests a Microsoft Defender quick scan in the background and opens a safety-triage Codex thread in parallel
- Both actions are intentionally light-touch: they launch safe workflows, not blind cleanup or destructive host actions

## Sensing Model

The pod derives its state from observable Codex runtime signals:

- `thinking`: only in root-work cases with no stronger child-path evidence; it prefers a fresh rollout reasoning hit and otherwise falls back to sustained `codex.exe app-server` CPU
- `tooling`: descendant activity must look meaningful, not just like shell presence; live child-path evidence keeps `thinking` suppressed
- `building`: descendant commands must look compile/bundle/build-like and actually be active
- `waiting`: descendant processes still exist, but only after earlier meaningful work has gone quiet
- `delivered`: short handoff glow after visible work settles
- `idle`: the default whenever signals are weak or ambiguous

## Diagnostics

Diagnostics are optional and live outside the main companion so the desktop presence stays clean. The diagnostics window shows:

- current derived state
- strongest candidate state when it lost the confidence gate
- activity hint
- reasoning string
- rollout reasoning hit or miss, age, and source
- last active process source
- poll generation / inflight generation
- root CPU delta
- descendant counts broken into meaningful, shell, build, and quiet buckets
- rolling sensor trace with recent polls, chosen/candidate state, and rejected reasons
- last error

Live validation on 2026-04-20 confirmed the diagnostics surface can show a real rollout-backed `thinking` transition, clear back out after the answer lands, and still suppress `thinking` when a live child tool path is present.
When diagnostics are hidden, the companion now skips rebuilding the diagnostics text until that window is shown again.
When no live `codex.exe app-server` is present, the poll loop now backs off slightly to reduce idle overhead.

## Notes

- Pure standard-library Python
- Built for Windows desktop use
