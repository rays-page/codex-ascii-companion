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
- Right click: menu with pause and quit
- Working state: driven by active child processes under `codex.exe app-server`
- Idle state: Codex is open but not actively running visible agent work

## Notes

- Pure standard-library Python
- Built for Windows desktop use
