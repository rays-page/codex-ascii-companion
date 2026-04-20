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
- Right click: redock, pause/resume sensing, diagnostics toggle, quit
- Pause/resume: clears stale snapshots and forces a fresh resync against the current Codex process tree
- Position: remembers the last dragged location and whether the pod was docked

## Sensing Model

The pod derives its state from observable Codex runtime signals:

- `thinking`: `codex.exe app-server` itself is active but there is no stronger tool/process signal
- `tooling`: real descendant processes are active under the Codex app-server tree
- `building`: descendant commands look like compile/bundle/build work
- `waiting`: descendant processes still exist but have gone quiet long enough to read as waiting
- `delivered`: short handoff glow after visible work settles
- `idle`: `standing by`

## Diagnostics

Diagnostics are optional and live outside the main companion so the desktop presence stays clean. The diagnostics window shows:

- current derived state
- activity hint
- reasoning string
- last active process source
- poll generation / inflight generation
- root CPU delta
- descendant counts
- last error

## Notes

- Pure standard-library Python
- Built for Windows desktop use
