from __future__ import annotations

from ctypes import wintypes
from pathlib import Path
import ctypes
import json
import os
import struct
import subprocess
import threading
import time
import tkinter as tk
import tkinter.font as tkfont


SPI_GETWORKAREA = 0x0030
POLL_MS = 700
FRAME_MS = 260
BUSY_HOLD_SECONDS = 1.6
ERROR_HOLD_SECONDS = 6.0
TRANSPARENT_KEY = "#010203"
HIT_PAD_X = 3
HIT_PAD_Y = 2
GWL_WNDPROC = -4
WM_NCHITTEST = 0x0084
HTCLIENT = 1
HTTRANSPARENT = -1
IGNORED_CODEX_CHILD_STEMS = {"conhost"}
IGNORED_CODEX_COMMAND_SNIPPETS = ("-encodedcommand",)
STATE_QUOTES = {
    "boot": "syncing",
    "idle": "standing by",
    "ping": "with you",
    "paused": "sensing off",
    "error": "lost sync",
}
ART_SHADOW_COLOR = "#223326"
QUOTE_SHADOW_COLOR = "#203024"
STATE_ART_COLORS = {
    "boot": "#c8e6ff",
    "idle": "#c8ffab",
    "working": "#fff0a8",
    "ping": "#ffdca1",
    "paused": "#d0d6d0",
    "error": "#ffb0a8",
}
STATE_QUOTE_COLORS = {
    "boot": "#88a9c4",
    "idle": "#8ba774",
    "working": "#c3b66b",
    "ping": "#c49a6e",
    "paused": "#8c928d",
    "error": "#d18a81",
}


def frame(*lines: str) -> str:
    return "\n".join(lines)


BOOT_FRAMES = (
    frame(
        " .__.",
        " |..|",
        " |_ |",
        " '=='",
    ),
    frame(
        " .__.",
        " |.:|",
        " |_ |",
        " '=='",
    ),
    frame(
        " .__.",
        " |..|",
        " |_.|",
        " '=='",
    ),
)

IDLE_FRAMES = (
    frame(
        " .__.",
        " |oo|",
        " |_>|",
        " '=='",
    ),
    frame(
        " .__.",
        " |-o|",
        " |_>|",
        " '=='",
    ),
)

WORKING_FRAMES = (
    frame(
        " .__.",
        " |><|",
        " |#>|",
        " '=#'",
    ),
    frame(
        " .__.",
        " |<>|",
        " |=.|",
        " '#='",
    ),
    frame(
        " .__.",
        " |><|",
        " |=>|",
        " '=#'",
    ),
    frame(
        " .__.",
        " |<>|",
        " |#>|",
        " '#='",
    ),
)

PING_FRAMES = (
    frame(
        " .__.",
        " |^^|",
        " |_>|",
        " '=='",
    ),
    frame(
        " .__.",
        " |^o|",
        " |_>|",
        " '=='",
    ),
)

PAUSED_FRAME = frame(
    " .__.",
    " |- |",
    " |z>|",
    " '=='",
)

ERROR_FRAME = frame(
    " .__.",
    " |xx|",
    " |!>|",
    " '=='",
)


def windows_work_area() -> tuple[int, int, int, int] | None:
    try:
        rect = wintypes.RECT()
        success = ctypes.windll.user32.SystemParametersInfoW(
            SPI_GETWORKAREA,
            0,
            ctypes.byref(rect),
            0,
        )
    except Exception:
        return None
    if not success:
        return None
    return rect.left, rect.top, rect.right, rect.bottom


def _set_pixel(pixels: list[list[tuple[int, int, int, int]]], x: int, y: int, color: tuple[int, int, int, int]) -> None:
    if 0 <= x < 32 and 0 <= y < 32:
        pixels[y][x] = color


def _fill_rect(
    pixels: list[list[tuple[int, int, int, int]]],
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: tuple[int, int, int, int],
) -> None:
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            _set_pixel(pixels, x, y, color)


def _fill_circle(
    pixels: list[list[tuple[int, int, int, int]]],
    cx: int,
    cy: int,
    radius: int,
    color: tuple[int, int, int, int],
) -> None:
    radius_sq = radius * radius
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= radius_sq:
                _set_pixel(pixels, x, y, color)


def _draw_line(
    pixels: list[list[tuple[int, int, int, int]]],
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: tuple[int, int, int, int],
    thickness: int = 1,
) -> None:
    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy
    x = x1
    y = y1
    while True:
        half = thickness // 2
        for oy in range(-half, half + 1):
            for ox in range(-half, half + 1):
                _set_pixel(pixels, x + ox, y + oy, color)
        if x == x2 and y == y2:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def _write_icon(path: Path) -> None:
    transparent = (0, 0, 0, 0)
    pod = (18, 32, 24, 255)
    accent = (96, 228, 164, 255)
    glow = (212, 255, 181, 255)
    deep = (9, 17, 13, 255)

    pixels = [[transparent for _ in range(32)] for _ in range(32)]

    _fill_circle(pixels, 16, 14, 10, pod)
    _fill_rect(pixels, 6, 9, 26, 20, pod)
    _fill_rect(pixels, 8, 10, 24, 16, deep)
    _fill_circle(pixels, 12, 13, 2, glow)
    _fill_circle(pixels, 20, 13, 2, glow)
    _draw_line(pixels, 13, 17, 19, 17, accent, thickness=1)
    _fill_circle(pixels, 16, 22, 3, accent)
    _draw_line(pixels, 11, 22, 7, 26, accent, thickness=2)
    _draw_line(pixels, 21, 22, 25, 26, accent, thickness=2)
    _draw_line(pixels, 14, 24, 12, 30, accent, thickness=2)
    _draw_line(pixels, 18, 24, 20, 30, accent, thickness=2)
    _draw_line(pixels, 7, 30, 25, 30, pod, thickness=1)
    _draw_line(pixels, 9, 4, 12, 1, accent, thickness=1)
    _fill_circle(pixels, 13, 1, 1, glow)

    width = 32
    height = 32
    xor_rows = []
    for y in range(height - 1, -1, -1):
        row = bytearray()
        for x in range(width):
            red, green, blue, alpha = pixels[y][x]
            row.extend((blue, green, red, alpha))
        xor_rows.append(bytes(row))
    xor_bitmap = b"".join(xor_rows)

    mask_stride = ((width + 31) // 32) * 4
    and_mask = b"\x00" * (mask_stride * height)

    header_size = 40
    image_size = header_size + len(xor_bitmap) + len(and_mask)
    icon_dir = struct.pack("<HHH", 0, 1, 1)
    icon_entry = struct.pack("<BBBBHHII", width, height, 0, 0, 1, 32, image_size, 22)
    dib_header = struct.pack(
        "<IIIHHIIIIII",
        header_size,
        width,
        height * 2,
        1,
        32,
        0,
        len(xor_bitmap) + len(and_mask),
        0,
        0,
        0,
        0,
    )

    path.write_bytes(icon_dir + icon_entry + dib_header + xor_bitmap + and_mask)


class CompanionApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Codex Courier Pod")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        try:
            self.root.wm_attributes("-toolwindow", True)
        except tk.TclError:
            pass
        self.root.configure(bg=TRANSPARENT_KEY)
        try:
            self.root.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        except tk.TclError:
            pass

        self.script_dir = Path(__file__).resolve().parent
        self.icon_path = self.script_dir / "codex_courier_pod.ico"
        _write_icon(self.icon_path)
        try:
            self.root.iconbitmap(default=str(self.icon_path))
        except tk.TclError:
            pass

        self.drag_offset = (0, 0)
        self.drag_start = (0, 0)
        self.drag_moved = False
        self.paused = False
        self._start_time = time.monotonic()
        self.busy_until = 0.0
        self.error_until = 0.0
        self.activity_hint = ""
        self.frame_index = 0
        self.last_snapshot: dict[int, tuple[str, float, str, int]] = {}
        self.self_pid = os.getpid()
        self.poll_generation = 0
        self.inflight_generation: int | None = None
        self.nudge_until = 0.0
        self.hit_rects: list[tuple[int, int, int, int]] = []
        self._wndproc = None
        self._old_wndproc = None
        self._set_window_long_ptr = None
        self._call_window_proc = None
        self._long_ptr_type = None

        self._build_ui()
        self._bind_events()
        self._install_hit_test_hook()
        self._dock_above_clock()
        self.root.after(160, self._animate)
        self.root.after(0, self._schedule_poll)

    def _build_ui(self) -> None:
        self.art_font = tkfont.Font(family="Consolas", size=9, weight="bold")
        self.quote_font = tkfont.Font(family="Consolas", size=7)
        initial_art = BOOT_FRAMES[0]
        width, height = self._measure_text(initial_art, self.art_font)

        self.canvas = tk.Canvas(
            self.root,
            width=width + 4,
            height=height + 16,
            bg=TRANSPARENT_KEY,
            highlightthickness=0,
            bd=0,
            relief="flat",
            cursor="hand2",
        )
        self.shadow_far_item = self.canvas.create_text(
            0,
            0,
            text="",
            fill=ART_SHADOW_COLOR,
            font=self.art_font,
            anchor="nw",
            justify="left",
        )
        self.shadow_near_item = self.canvas.create_text(
            1,
            1,
            text=initial_art,
            fill=ART_SHADOW_COLOR,
            font=self.art_font,
            anchor="nw",
            justify="left",
        )
        self.art_item = self.canvas.create_text(
            0,
            0,
            text=initial_art,
            fill=STATE_ART_COLORS["boot"],
            font=self.art_font,
            anchor="nw",
            justify="left",
        )
        self.quote_shadow_item = self.canvas.create_text(
            1,
            height + 4,
            text=STATE_QUOTES["boot"],
            fill=QUOTE_SHADOW_COLOR,
            font=self.quote_font,
            anchor="nw",
            justify="left",
        )
        self.quote_item = self.canvas.create_text(
            0,
            height + 3,
            text=STATE_QUOTES["boot"],
            fill=STATE_QUOTE_COLORS["boot"],
            font=self.quote_font,
            anchor="nw",
            justify="left",
        )
        self.canvas.pack(anchor="w", padx=1, pady=1)
        self._set_display("boot", initial_art)

        self.menu = tk.Menu(self.root, tearoff=False)
        self.menu.add_command(label="Redock Above Clock", command=self._dock_above_clock)
        self.menu.add_command(label="Pause Sensing", command=self._toggle_pause)
        self.menu.add_separator()
        self.menu.add_command(label="Quit Courier Pod", command=self.root.destroy)

        self.root.update_idletasks()

    def _bind_events(self) -> None:
        for widget in (self.root, self.canvas):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._drag)
            widget.bind("<ButtonRelease-1>", self._end_click)
            widget.bind("<Double-Button-1>", self._double_click)
            widget.bind("<Button-3>", self._show_menu)

    def _start_drag(self, event: tk.Event[tk.Misc]) -> None:
        self.drag_offset = (event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y())
        self.drag_start = (event.x_root, event.y_root)
        self.drag_moved = False

    def _drag(self, event: tk.Event[tk.Misc]) -> None:
        if abs(event.x_root - self.drag_start[0]) + abs(event.y_root - self.drag_start[1]) >= 3:
            self.drag_moved = True
        x = event.x_root - self.drag_offset[0]
        y = event.y_root - self.drag_offset[1]
        self.root.geometry(f"+{x}+{y}")

    def _end_click(self, _event: tk.Event[tk.Misc]) -> None:
        if not self.drag_moved:
            self.nudge_until = time.monotonic() + 1.2

    def _double_click(self, _event: tk.Event[tk.Misc]) -> None:
        self.nudge_until = time.monotonic() + 1.2
        self._dock_above_clock()

    def _show_menu(self, event: tk.Event[tk.Misc]) -> None:
        self.nudge_until = time.monotonic() + 1.2
        self.menu.entryconfigure(1, label="Resume Sensing" if self.paused else "Pause Sensing")
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _dock_above_clock(self) -> None:
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        area = windows_work_area()
        if area is None:
            right = self.root.winfo_screenwidth()
            bottom = self.root.winfo_screenheight()
        else:
            _, _, right, bottom = area
        x = right - width - 14
        y = bottom - height - 8
        self.root.geometry(f"+{x}+{y}")

    def _toggle_pause(self) -> None:
        self.paused = not self.paused
        self.activity_hint = ""
        self.busy_until = 0.0
        self.error_until = 0.0
        self.last_snapshot.clear()
        self.poll_generation += 1
        self.frame_index = 0
        if not self.paused:
            self.root.after(0, self._schedule_poll)

    def _current_state(self) -> str:
        now = time.monotonic()
        if self.paused:
            return "paused"
        if now < self.error_until:
            return "error"
        if now < self.nudge_until:
            return "ping"
        if now < self.busy_until:
            return "working"
        if now < self.start_time + 2.2:
            return "boot"
        return "idle"

    def _frames_for_state(self, state: str) -> tuple[str, ...]:
        if state == "boot":
            return BOOT_FRAMES
        if state == "working":
            return WORKING_FRAMES
        if state == "ping":
            return PING_FRAMES
        if state == "paused":
            return (PAUSED_FRAME,)
        if state == "error":
            return (ERROR_FRAME,)
        return IDLE_FRAMES

    def _measure_text(self, text: str, font: tkfont.Font) -> tuple[int, int]:
        lines = text.splitlines() or [""]
        width = max(font.measure(line) for line in lines)
        height = font.metrics("linespace") * len(lines)
        return width, height

    def _quote_for_state(self, state: str) -> str:
        if state == "working":
            return self._working_quote()
        return STATE_QUOTES.get(state, "")

    def _working_quote(self) -> str:
        hint = self.activity_hint.lower()
        if hint in {"powershell", "cmd"}:
            return "in shell"
        if hint in {"python", "py"}:
            return "on python"
        if hint in {"git"}:
            return "on git"
        if hint in {"node", "npm", "pnpm"}:
            return "on node"
        if hint in {"cargo", "rustc", "gcc", "msbuild", "devenv"}:
            return "building"
        return "at work"

    def _visible_line_bounds(self, line: str, font: tkfont.Font) -> tuple[int, int] | None:
        if not line.strip():
            return None
        first = next(index for index, char in enumerate(line) if char != " ")
        last = len(line.rstrip()) - 1
        return font.measure(line[:first]), font.measure(line[: last + 1])

    def _point_in_hit_shape(self, x: int, y: int) -> bool:
        for left, top, right, bottom in self.hit_rects:
            if left <= x < right and top <= y < bottom:
                return True
        return False

    def _install_hit_test_hook(self) -> None:
        if os.name != "nt":
            return
        long_ptr = ctypes.c_longlong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long
        wndproc_type = ctypes.WINFUNCTYPE(long_ptr, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
        user32 = ctypes.windll.user32
        user32.SetWindowLongPtrW.restype = long_ptr
        user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, long_ptr]
        user32.CallWindowProcW.restype = long_ptr
        user32.CallWindowProcW.argtypes = [long_ptr, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        self._set_window_long_ptr = user32.SetWindowLongPtrW
        self._call_window_proc = user32.CallWindowProcW
        self._long_ptr_type = long_ptr

        def wndproc(hwnd: int, msg: int, wparam: int, lparam: int) -> int:
            if msg == WM_NCHITTEST:
                x = ctypes.c_short(lparam & 0xFFFF).value - self.root.winfo_rootx()
                y = ctypes.c_short((lparam >> 16) & 0xFFFF).value - self.root.winfo_rooty()
                if self._point_in_hit_shape(x, y):
                    return HTCLIENT
                return HTTRANSPARENT
            return self._call_window_proc(self._old_wndproc, hwnd, msg, wparam, lparam)

        self._wndproc = wndproc_type(wndproc)
        self._old_wndproc = self._set_window_long_ptr(
            self.root.winfo_id(),
            GWL_WNDPROC,
            long_ptr(ctypes.cast(self._wndproc, ctypes.c_void_p).value),
        )
        self.root.bind("<Destroy>", self._restore_hit_test_hook, add=True)

    def _restore_hit_test_hook(self, event: tk.Event[tk.Misc]) -> None:
        if event.widget is not self.root:
            return
        if not (self._old_wndproc and self._set_window_long_ptr and self._long_ptr_type):
            return
        try:
            self._set_window_long_ptr(
                self.root.winfo_id(),
                GWL_WNDPROC,
                self._long_ptr_type(self._old_wndproc),
            )
        except Exception:
            pass
        finally:
            self._old_wndproc = None

    def _update_hit_shape(self, art: str, quote: str, art_x: int, quote_x: int, quote_y: int) -> None:
        rects: list[tuple[int, int, int, int]] = []
        region_specs = (
            (art.splitlines() or [""], self.art_font, art_x, 2),
            ((quote.splitlines() or [""]) if quote else [], self.quote_font, quote_x, quote_y),
        )
        for lines, font, x_origin, y_origin in region_specs:
            line_height = font.metrics("linespace")
            for row, line in enumerate(lines):
                bounds = self._visible_line_bounds(line, font)
                if bounds is None:
                    continue
                left, right = bounds
                top = y_origin + (row * line_height)
                rects.append(
                    (
                        x_origin + left - HIT_PAD_X,
                        top - HIT_PAD_Y,
                        x_origin + right + HIT_PAD_X + 3,
                        top + line_height + HIT_PAD_Y + 3,
                    )
                )
        self.hit_rects = rects

    def _set_display(self, state: str, art: str) -> None:
        art_width, art_height = self._measure_text(art, self.art_font)
        quote = self._quote_for_state(state)
        quote_width, quote_height = self._measure_text(quote, self.quote_font) if quote else (0, 0)
        content_width = max(art_width, quote_width)
        content_height = art_height + (quote_height + 4 if quote else 0)
        pad_x = 2
        pad_y = 2
        art_x = pad_x + (content_width - art_width) // 2
        quote_x = pad_x + (content_width - quote_width) // 2 if quote else pad_x
        quote_y = pad_y + art_height + 3
        self.canvas.configure(width=content_width + 4, height=content_height + 4)
        self.canvas.itemconfigure(self.shadow_far_item, text="")
        self.canvas.itemconfigure(self.shadow_near_item, text=art, fill=ART_SHADOW_COLOR)
        self.canvas.itemconfigure(self.art_item, text=art, fill=STATE_ART_COLORS[state])
        self.canvas.coords(self.shadow_far_item, 0, 0)
        self.canvas.coords(self.shadow_near_item, art_x + 1, pad_y + 1)
        self.canvas.coords(self.art_item, art_x, pad_y)
        self.canvas.itemconfigure(self.quote_shadow_item, text=quote, fill=QUOTE_SHADOW_COLOR)
        self.canvas.itemconfigure(self.quote_item, text=quote, fill=STATE_QUOTE_COLORS[state])
        self.canvas.coords(self.quote_shadow_item, quote_x + 1, quote_y + 1)
        self.canvas.coords(self.quote_item, quote_x, quote_y)
        self._update_hit_shape(art, quote, art_x, quote_x, quote_y)

    def _animate(self) -> None:
        state = self._current_state()
        frames = self._frames_for_state(state)
        self.frame_index = (self.frame_index + 1) % len(frames)
        self._set_display(state, frames[self.frame_index])
        self.root.after(FRAME_MS, self._animate)

    @property
    def start_time(self) -> float:
        return self._start_time

    def _schedule_poll(self) -> None:
        if self.paused:
            return
        if self.inflight_generation == self.poll_generation:
            self.root.after(POLL_MS, self._schedule_poll)
            return
        generation = self.poll_generation
        self.inflight_generation = generation
        worker = threading.Thread(target=self._poll_processes, args=(generation,), daemon=True)
        worker.start()

    def _poll_processes(self, generation: int) -> None:
        command = (
            "$cpuById = @{}; "
            "Get-Process | ForEach-Object { "
            "$cpuById[[int]$_.Id] = if ($null -eq $_.CPU) { 0.0 } else { [double]$_.CPU } "
            "}; "
            "$items = @(Get-CimInstance Win32_Process | Select-Object "
            "ProcessId, ParentProcessId, Name, CommandLine, "
            "@{Name='CPU';Expression={ if ($cpuById.ContainsKey([int]$_.ProcessId)) { $cpuById[[int]$_.ProcessId] } else { 0.0 } }}); "
            "if ($items.Count -eq 0) { '[]' } else { $items | ConvertTo-Json -Compress }"
        )
        try:
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", command],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or "Get-Process failed")
            snapshot = self._normalize_snapshot(completed.stdout.strip())
            active_name = self._compute_activity(snapshot)
            error_text = ""
        except Exception as exc:  # noqa: BLE001
            active_name = ""
            error_text = str(exc)
        self.root.after(0, lambda: self._apply_poll_result(generation, active_name, error_text))

    def _normalize_snapshot(self, payload: str) -> list[dict[str, object]]:
        if not payload:
            return []
        data = json.loads(payload)
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        return []

    def _process_stem(self, name: str) -> str:
        return Path(name).stem.lower()

    def _hint_from_process(self, stem: str, command_line: str) -> str:
        lowered = command_line.lower()
        if stem in {"powershell", "cmd"}:
            for tool_name in ("git", "python", "py", "node", "npm", "pnpm", "cargo", "rustc", "msbuild", "devenv", "uv"):
                if tool_name in lowered:
                    return tool_name
        return stem

    def _is_codex_root(self, name: str, command_line: str) -> bool:
        return self._process_stem(name) == "codex" and "app-server" in command_line.lower()

    def _ignore_codex_child(self, stem: str, command_line: str) -> bool:
        lowered = command_line.lower()
        return stem in IGNORED_CODEX_CHILD_STEMS or any(snippet in lowered for snippet in IGNORED_CODEX_COMMAND_SNIPPETS)

    def _compute_activity(self, snapshot: list[dict[str, object]]) -> str:
        next_snapshot: dict[int, tuple[str, float, str, int]] = {}
        children_by_parent: dict[int, list[int]] = {}
        roots: list[int] = []
        for item in snapshot:
            try:
                pid = int(item.get("ProcessId", item.get("Id", 0)))
            except (TypeError, ValueError):
                continue
            if pid == self.self_pid:
                continue
            name = str(item.get("Name", item.get("ProcessName", "")) or "").strip()
            if not name:
                continue
            command_line = str(item.get("CommandLine", "") or "")
            try:
                parent_pid = int(item.get("ParentProcessId", 0) or 0)
            except (TypeError, ValueError):
                parent_pid = 0
            try:
                cpu = float(item.get("CPU", 0.0) or 0.0)
            except (TypeError, ValueError):
                cpu = 0.0
            next_snapshot[pid] = (name, cpu, command_line, parent_pid)
            children_by_parent.setdefault(parent_pid, []).append(pid)
            if self._is_codex_root(name, command_line):
                roots.append(pid)

        active_hint = ""
        best_score = 0.0
        best_hint = ""
        seen: set[int] = set()
        queue = list(roots)
        while queue:
            current_pid = queue.pop(0)
            if current_pid in seen:
                continue
            seen.add(current_pid)
            queue.extend(children_by_parent.get(current_pid, ()))

        for pid in seen:
            if pid in roots:
                continue
            name, cpu, command_line, _parent_pid = next_snapshot[pid]
            stem = self._process_stem(name)
            if self._ignore_codex_child(stem, command_line):
                continue
            hint = self._hint_from_process(stem, command_line)
            previous = self.last_snapshot.get(pid)
            if previous is None:
                score = 0.08
            else:
                score = max(cpu - previous[1], 0.0)
            if score > best_score and score >= 0.03:
                active_hint = hint
                best_score = score
            if not best_hint:
                best_hint = hint
        if not active_hint:
            active_hint = best_hint

        self.last_snapshot = next_snapshot
        return active_hint

    def _apply_poll_result(self, generation: int, active_name: str, error_text: str) -> None:
        if self.inflight_generation == generation:
            self.inflight_generation = None
        if generation != self.poll_generation:
            if not self.paused:
                self.root.after(0, self._schedule_poll)
            return
        if error_text:
            self.error_until = time.monotonic() + ERROR_HOLD_SECONDS
        else:
            self.error_until = 0.0
            if active_name:
                self.activity_hint = active_name
                self.busy_until = time.monotonic() + BUSY_HOLD_SECONDS
            elif time.monotonic() >= self.busy_until:
                self.activity_hint = ""
        self.root.after(POLL_MS, self._schedule_poll)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = CompanionApp()
    app.run()


if __name__ == "__main__":
    main()
