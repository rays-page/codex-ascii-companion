# Codex ASCII Companion

Small transparent desktop companion for Windows.

It sits above the taskbar clock, uses tiny pixel-style ASCII states, and reacts to real Codex agent work instead of just the Codex window being open.

## Files

- `codex_ascii_companion.pyw`: standalone app
- `codex_courier_pod.ico`: generated icon used by the window and shortcut

## Run

Use the Desktop shortcut, or run:

```powershell
pythonw .\codex_ascii_companion.pyw
```

## Behavior

- Left click: little acknowledgement animation
- Double click: redock above the clock
- Right click: menu with pause, resume, and quit
- Working state: driven by active child processes under `codex.exe app-server`
- Idle state: shown as `standing by` when Codex is not actively running visible agent work
- Resume sensing: clears stale state and immediately resyncs with the current Codex process tree

## Notes

- Pure standard-library Python
- Built for Windows desktop use
