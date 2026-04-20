from __future__ import annotations

from collections import deque
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path
import ctypes
import json
import os
import struct
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont


SPI_GETWORKAREA = 0x0030
POLL_MS = 550
FRAME_MS = 220
BOOT_SECONDS = 1.6
PING_SECONDS = 1.2
THINKING_HOLD_SECONDS = 1.4
WAITING_GRACE_SECONDS = 2.8
DELIVERED_HOLD_SECONDS = 2.0
ERROR_HOLD_SECONDS = 6.0
NEW_PROCESS_BONUS = 0.06
ACTIVE_CPU_THRESHOLD = 0.015
ROOT_THINKING_CPU_THRESHOLD = 0.05
ROOT_THINKING_MIN_STREAK = 2
SETTINGS_FILENAME = "companion_settings.json"
DEBUG_LOG_LIMIT = 16
TRANSPARENT_KEY = "#010203"
HIT_PAD_X = 3
HIT_PAD_Y = 2
GWL_WNDPROC = -4
WM_NCHITTEST = 0x0084
HTCLIENT = 1
HTTRANSPARENT = -1
IGNORED_CODEX_CHILD_STEMS = {"conhost"}
IGNORED_CODEX_COMMAND_SNIPPETS = ("-encodedcommand",)
SHELL_STEMS = {"powershell", "pwsh", "cmd"}
BUILD_TOOL_STEMS = {
    "cargo",
    "clang",
    "clang++",
    "cl",
    "cmake",
    "devenv",
    "gcc",
    "g++",
    "gradle",
    "link",
    "make",
    "msbuild",
    "mvn",
    "next",
    "ninja",
    "rustc",
    "tsc",
    "vite",
    "webpack",
}
BUILD_COMMAND_SNIPPETS = (
    " build",
    " compile",
    " py_compile",
    "msbuild",
    "devenv",
    "cmake",
    "ninja",
    "cargo",
    "rustc",
    "webpack",
    "vite",
    "tsc",
    "next build",
)
TOOL_HINT_ORDER = (
    "msbuild",
    "devenv",
    "cmake",
    "ninja",
    "cargo",
    "rustc",
    "webpack",
    "vite",
    "tsc",
    "pytest",
    "python",
    "node",
    "pnpm",
    "npm",
    "yarn",
    "next",
    "git",
    "uv",
    "pip",
    "py",
)
HINT_ALIASES = {
    "pythonw": "python",
}
ACTIVE_VISUAL_STATES = {"thinking", "tooling", "building", "waiting"}
STATE_QUOTES = {
    "boot": "syncing",
    "idle": "standing by",
    "thinking": "thinking",
    "tooling": "in tools",
    "building": "building",
    "waiting": "holding",
    "delivered": "ready",
    "ping": "with you",
    "paused": "sensing off",
    "error": "lost sync",
}
ART_SHADOW_COLOR = "#223326"
QUOTE_SHADOW_COLOR = "#203024"
STATE_ART_COLORS = {
    "boot": "#c8e6ff",
    "idle": "#c8ffab",
    "thinking": "#cfe6ff",
    "tooling": "#fff0a8",
    "building": "#ffd3a0",
    "waiting": "#cad8ff",
    "delivered": "#bbffbf",
    "ping": "#ffdca1",
    "paused": "#d0d6d0",
    "error": "#ffb0a8",
}
STATE_QUOTE_COLORS = {
    "boot": "#88a9c4",
    "idle": "#8ba774",
    "thinking": "#8faec5",
    "tooling": "#c3b66b",
    "building": "#d8a56e",
    "waiting": "#99aacd",
    "delivered": "#8fbf8e",
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

THINKING_FRAMES = (
    frame(
        " .__.",
        " |..|",
        " |:>|",
        " '=='",
    ),
    frame(
        " .__.",
        " |.:|",
        " |:>|",
        " '=='",
    ),
    frame(
        " .__.",
        " |:.|",
        " |:>|",
        " '=='",
    ),
)

TOOLING_FRAMES = (
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

BUILDING_FRAMES = (
    frame(
        " .__.",
        " |**|",
        " |#>|",
        " '##'",
    ),
    frame(
        " .__.",
        " |##|",
        " |^>|",
        " '#*'",
    ),
    frame(
        " .__.",
        " |*#|",
        " |#>|",
        " '*#'",
    ),
)

WAITING_FRAMES = (
    frame(
        " .__.",
        " |--|",
        " |~>|",
        " '=='",
    ),
    frame(
        " .__.",
        " |..|",
        " |~>|",
        " '=='",
    ),
)

DELIVERED_FRAMES = (
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


@dataclass(slots=True)
class ProcessSample:
    name: str
    cpu: float
    command_line: str
    parent_pid: int


@dataclass(slots=True)
class ActivitySnapshot:
    descendants: int = 0
    hot_descendants: int = 0
    new_descendants: int = 0
    root_pid: int | None = None
    root_cpu_delta: float = 0.0
    hint: str = ""
    phase_kind: str = "-"
    source_pid: int | None = None
    source_name: str = ""
    source_command: str = ""
    reason: str = "quiet"


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
        self.script_dir = Path(__file__).resolve().parent
        self.icon_path = self.script_dir / "codex_courier_pod.ico"
        self.settings_path = self.script_dir / SETTINGS_FILENAME
        self.cli_debug_requested = "--debug" in sys.argv[1:]
        self.settings_error = ""
        self.settings = self._load_settings()

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

        _write_icon(self.icon_path)
        try:
            self.root.iconbitmap(default=str(self.icon_path))
        except tk.TclError:
            pass

        self.drag_offset = (0, 0)
        self.drag_start = (0, 0)
        self.drag_moved = False
        self.paused = False
        self.docked = bool(self._window_settings().get("docked", True))
        self.debug_visible = bool(self.settings.get("debug", False) or self.cli_debug_requested)
        self._start_time = time.monotonic()
        self.last_snapshot: dict[int, ProcessSample] = {}
        self.self_pid = os.getpid()
        self.poll_generation = 0
        self.inflight_generation: int | None = None
        self.nudge_until = 0.0
        self.error_until = 0.0
        self.delivered_until = 0.0
        self.last_tool_activity_at = 0.0
        self.last_root_activity_at = 0.0
        self.root_activity_streak = 0
        self.last_descendant_seen_at = 0.0
        self.last_successful_poll_at = 0.0
        self.activity_hint = ""
        self.visual_state = "boot"
        self.last_state_reason = "booting"
        self.last_active_source = ""
        self.last_error_text = self.settings_error
        self.root_pid: int | None = None
        self.root_cpu_delta = 0.0
        self.last_sample = ActivitySnapshot(reason="booting")
        self.debug_messages: deque[str] = deque(maxlen=DEBUG_LOG_LIMIT)
        self.hit_rects: list[tuple[int, int, int, int]] = []
        self._wndproc = None
        self._old_wndproc = None
        self._set_window_long_ptr = None
        self._call_window_proc = None
        self._long_ptr_type = None
        self.debug_summary_var = tk.StringVar(master=self.root, value="")
        self.debug_log_var = tk.StringVar(master=self.root, value="")
        self.debug_window: tk.Toplevel | None = None

        self._build_ui()
        self._bind_events()
        self._install_hit_test_hook()
        self._restore_saved_geometry()
        if self.debug_visible:
            self._ensure_debug_window()
            self.root.after(120, self._place_debug_window)
        if self.settings_error:
            self._log_debug(f"settings load failed: {self.settings_error}")
        self._log_debug("sensor online")
        self.root.after(140, self._animate)
        self.root.after(0, self._schedule_poll)

    def _load_settings(self) -> dict[str, object]:
        settings: dict[str, object] = {
            "version": 1,
            "debug": False,
            "window": {
                "docked": True,
                "x": None,
                "y": None,
            },
        }
        if not self.settings_path.exists():
            return settings
        try:
            payload = json.loads(self.settings_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            self.settings_error = str(exc)
            return settings
        if not isinstance(payload, dict):
            self.settings_error = "settings root must be an object"
            return settings

        if isinstance(payload.get("debug"), bool):
            settings["debug"] = payload["debug"]

        window_payload = payload.get("window")
        if isinstance(window_payload, dict):
            window_settings = settings["window"]
            if isinstance(window_payload.get("docked"), bool):
                window_settings["docked"] = window_payload["docked"]
            for key in ("x", "y"):
                value = window_payload.get(key)
                if isinstance(value, int):
                    window_settings[key] = value
        return settings

    def _window_settings(self) -> dict[str, object]:
        window_settings = self.settings.get("window")
        if isinstance(window_settings, dict):
            return window_settings
        window_settings = {"docked": True, "x": None, "y": None}
        self.settings["window"] = window_settings
        return window_settings

    def _save_settings(self) -> None:
        window_settings = self._window_settings()
        window_settings["docked"] = self.docked
        if self.root.winfo_exists():
            window_settings["x"] = int(self.root.winfo_x())
            window_settings["y"] = int(self.root.winfo_y())
        self.settings["debug"] = self.debug_visible
        try:
            self.settings_path.write_text(json.dumps(self.settings, indent=2) + "\n", encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            self.last_error_text = f"settings save failed: {exc}"
            self.error_until = time.monotonic() + ERROR_HOLD_SECONDS
            self._log_debug(self.last_error_text)

    def _restore_saved_geometry(self) -> None:
        self.root.update_idletasks()
        window_settings = self._window_settings()
        x = window_settings.get("x")
        y = window_settings.get("y")
        if self.docked or not isinstance(x, int) or not isinstance(y, int):
            self._dock_above_clock(save=False)
            return

        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        area = windows_work_area()
        if area is not None:
            left, top, right, bottom = area
            x = min(max(x, left), max(left, right - width))
            y = min(max(y, top), max(top, bottom - height))
        self.root.geometry(f"+{x}+{y}")
        self._place_debug_window()

    def _remember_window_position(self, *, docked: bool | None = None) -> None:
        if docked is not None:
            self.docked = docked
        self._save_settings()
        self._place_debug_window()

    def _build_ui(self) -> None:
        self.art_font = tkfont.Font(family="Consolas", size=9, weight="bold")
        self.quote_font = tkfont.Font(family="Consolas", size=7)
        self.debug_font = tkfont.Font(family="Consolas", size=8)
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
        self.pause_menu_index = 1
        self.menu.add_command(label="Show Diagnostics", command=self._toggle_debug_window)
        self.debug_menu_index = 2
        self.menu.add_separator()
        self.menu.add_command(label="Quit Courier Pod", command=self._quit)
        self._update_menu_labels()

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
        self.nudge_until = time.monotonic() + PING_SECONDS
        self._log_debug("acknowledged contact")

    def _drag(self, event: tk.Event[tk.Misc]) -> None:
        if abs(event.x_root - self.drag_start[0]) + abs(event.y_root - self.drag_start[1]) >= 3:
            self.drag_moved = True
            self.docked = False
        x = event.x_root - self.drag_offset[0]
        y = event.y_root - self.drag_offset[1]
        self.root.geometry(f"+{x}+{y}")
        self._place_debug_window()

    def _end_click(self, _event: tk.Event[tk.Misc]) -> None:
        if self.drag_moved:
            self._remember_window_position(docked=False)
            self._log_debug("moved pod")
            return
        self._log_debug("click released")

    def _double_click(self, _event: tk.Event[tk.Misc]) -> None:
        self.nudge_until = time.monotonic() + PING_SECONDS
        self._dock_above_clock()
        self._log_debug("redocked")

    def _show_menu(self, event: tk.Event[tk.Misc]) -> None:
        self.nudge_until = time.monotonic() + PING_SECONDS
        self._update_menu_labels()
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _update_menu_labels(self) -> None:
        self.menu.entryconfigure(self.pause_menu_index, label="Resume Sensing" if self.paused else "Pause Sensing")
        self.menu.entryconfigure(self.debug_menu_index, label="Hide Diagnostics" if self.debug_visible else "Show Diagnostics")

    def _dock_above_clock(self, *, save: bool = True) -> None:
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        area = windows_work_area()
        if area is None:
            right = self.root.winfo_screenwidth()
            bottom = self.root.winfo_screenheight()
        else:
            _, _, right, bottom = area
        x = right - width - 22
        y = bottom - height - 12
        self.root.geometry(f"+{x}+{y}")
        self.docked = True
        if save:
            self._remember_window_position(docked=True)
        else:
            self._place_debug_window()

    def _toggle_pause(self) -> None:
        self.paused = not self.paused
        self.activity_hint = ""
        self.delivered_until = 0.0
        self.error_until = 0.0
        self.last_snapshot.clear()
        self.last_tool_activity_at = 0.0
        self.last_root_activity_at = 0.0
        self.root_activity_streak = 0
        self.last_descendant_seen_at = 0.0
        self.root_pid = None
        self.root_cpu_delta = 0.0
        self.last_sample = ActivitySnapshot(reason="paused")
        self.last_active_source = ""
        self.poll_generation += 1
        self.inflight_generation = None
        if self.paused:
            self.visual_state = "paused"
            self.last_state_reason = "user paused sensing"
            self._log_debug("sensing paused")
        else:
            self.visual_state = "boot"
            self.last_state_reason = "resyncing"
            self._log_debug("resume and resync")
            self.root.after(0, self._schedule_poll)
        self._refresh_debug_view()

    def _toggle_debug_window(self) -> None:
        if self.debug_visible:
            self._hide_debug_window()
            return
        self.debug_visible = True
        self._ensure_debug_window()
        self._save_settings()
        self._update_menu_labels()
        self._log_debug("diagnostics shown")

    def _ensure_debug_window(self) -> None:
        if self.debug_window is not None and self.debug_window.winfo_exists():
            self._place_debug_window()
            self._refresh_debug_view()
            return

        self.debug_window = tk.Toplevel(self.root)
        self.debug_window.title("Courier Diagnostics")
        self.debug_window.configure(bg="#0c130f", highlightbackground="#243228", highlightthickness=1)
        self.debug_window.resizable(False, False)
        self.debug_window.attributes("-topmost", True)
        try:
            self.debug_window.wm_attributes("-toolwindow", True)
        except tk.TclError:
            pass
        try:
            self.debug_window.wm_attributes("-alpha", 0.96)
        except tk.TclError:
            pass

        summary_label = tk.Label(
            self.debug_window,
            textvariable=self.debug_summary_var,
            bg="#0c130f",
            fg="#d3e8c9",
            font=self.debug_font,
            justify="left",
            anchor="nw",
        )
        summary_label.pack(fill="both", expand=False, padx=10, pady=(10, 6))

        divider = tk.Frame(self.debug_window, height=1, bg="#243228", bd=0, highlightthickness=0)
        divider.pack(fill="x", padx=10, pady=(0, 6))

        log_label = tk.Label(
            self.debug_window,
            textvariable=self.debug_log_var,
            bg="#0c130f",
            fg="#7fa07b",
            font=self.debug_font,
            justify="left",
            anchor="nw",
        )
        log_label.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.debug_window.protocol("WM_DELETE_WINDOW", self._hide_debug_window)
        self._place_debug_window()
        self._refresh_debug_view()

    def _hide_debug_window(self) -> None:
        self.debug_visible = False
        if self.debug_window is not None and self.debug_window.winfo_exists():
            self.debug_window.destroy()
        self.debug_window = None
        self._save_settings()
        self._update_menu_labels()
        self._refresh_debug_view()

    def _place_debug_window(self) -> None:
        if self.debug_window is None or not self.debug_window.winfo_exists():
            return
        self.root.update_idletasks()
        self.debug_window.update_idletasks()
        width = self.debug_window.winfo_reqwidth()
        height = self.debug_window.winfo_reqheight()
        x = self.root.winfo_x() - width - 18
        y = max(self.root.winfo_y() - 10, 16)
        area = windows_work_area()
        if area is not None:
            left, top, right, bottom = area
            x = min(max(x, left + 8), max(left + 8, right - width - 8))
            y = min(max(y, top + 8), max(top + 8, bottom - height - 8))
        self.debug_window.geometry(f"+{x}+{y}")

    def _age_text(self, timestamp: float) -> str:
        if timestamp <= 0.0:
            return "-"
        return f"{max(time.monotonic() - timestamp, 0.0):.1f}s"

    def _refresh_debug_view(self) -> None:
        summary_lines = [
            f"state      {self._current_state()}",
            f"hint       {self.activity_hint or '-'}",
            f"reason     {self.last_state_reason or '-'}",
            f"source     {self.last_active_source or '-'}",
            f"poll gen   {self.poll_generation} / {self.inflight_generation if self.inflight_generation is not None else '-'}",
            f"root cpu   {self.root_cpu_delta:.3f} (pid {self.root_pid or '-'})",
            f"root gate  {self.root_activity_streak}/{ROOT_THINKING_MIN_STREAK} over {ROOT_THINKING_CPU_THRESHOLD:.3f}",
            f"desc       {self.last_sample.descendants} total, {self.last_sample.hot_descendants} hot, {self.last_sample.new_descendants} new",
            f"kind       {self.last_sample.phase_kind}",
            f"last poll  {self._age_text(self.last_successful_poll_at)} ago",
            f"error      {self.last_error_text or '-'}",
        ]
        self.debug_summary_var.set("\n".join(summary_lines))
        self.debug_log_var.set("\n".join(self.debug_messages) if self.debug_messages else "no events yet")

    def _log_debug(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.debug_messages.append(f"{timestamp} {message}")
        self._refresh_debug_view()

    def _quit(self) -> None:
        self._save_settings()
        self.root.destroy()

    def _current_state(self) -> str:
        now = time.monotonic()
        if self.paused:
            return "paused"
        if now < self.error_until:
            return "error"
        if now < self.nudge_until:
            return "ping"
        if self.visual_state == "boot" and now < self.start_time + BOOT_SECONDS:
            return "boot"
        return self.visual_state

    def _frames_for_state(self, state: str) -> tuple[str, ...]:
        if state == "boot":
            return BOOT_FRAMES
        if state == "thinking":
            return THINKING_FRAMES
        if state == "tooling":
            return TOOLING_FRAMES
        if state == "building":
            return BUILDING_FRAMES
        if state == "waiting":
            return WAITING_FRAMES
        if state == "delivered":
            return DELIVERED_FRAMES
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
        if state == "tooling":
            return self._tooling_quote()
        if state == "building":
            return self._building_quote()
        if state == "thinking":
            return STATE_QUOTES["thinking"]
        if state == "waiting":
            return STATE_QUOTES["waiting"]
        return STATE_QUOTES.get(state, "")

    def _tooling_quote(self) -> str:
        hint = self.activity_hint.lower()
        if hint in {"powershell", "pwsh", "cmd"}:
            return "in shell"
        if hint in {"python", "py", "uv", "pip"}:
            return "on python"
        if hint in {"git"}:
            return "on git"
        if hint in {"node", "npm", "pnpm", "yarn", "next"}:
            return "on node"
        return STATE_QUOTES["tooling"]

    def _building_quote(self) -> str:
        hint = self.activity_hint.lower()
        if hint in {"vite", "webpack", "next", "tsc"}:
            return "bundling"
        return STATE_QUOTES["building"]

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
        self.frame_index = (getattr(self, "frame_index", -1) + 1) % len(frames)
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
            activity = self._compute_activity(snapshot)
            error_text = ""
        except Exception as exc:  # noqa: BLE001
            activity = ActivitySnapshot(reason="poll failed")
            error_text = str(exc)
        self.root.after(0, lambda: self._apply_poll_result(generation, activity, error_text))

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
        return HINT_ALIASES.get(Path(name).stem.lower(), Path(name).stem.lower())

    def _hint_from_process(self, stem: str, command_line: str) -> str:
        lowered = command_line.lower()
        if stem in SHELL_STEMS:
            for tool_name in TOOL_HINT_ORDER:
                if tool_name in lowered:
                    return "python" if tool_name == "py" else tool_name
            return stem
        return stem

    def _classify_process_kind(self, stem: str, command_line: str, hint: str) -> str:
        lowered = command_line.lower()
        if stem in BUILD_TOOL_STEMS or hint in BUILD_TOOL_STEMS:
            return "build"
        if any(snippet in lowered for snippet in BUILD_COMMAND_SNIPPETS):
            return "build"
        return "tool"

    def _is_codex_root(self, name: str, command_line: str) -> bool:
        return self._process_stem(name) == "codex" and "app-server" in command_line.lower()

    def _ignore_codex_child(self, stem: str, command_line: str) -> bool:
        lowered = command_line.lower()
        return stem in IGNORED_CODEX_CHILD_STEMS or any(snippet in lowered for snippet in IGNORED_CODEX_COMMAND_SNIPPETS)

    def _compute_activity(self, snapshot: list[dict[str, object]]) -> ActivitySnapshot:
        next_snapshot: dict[int, ProcessSample] = {}
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

            next_snapshot[pid] = ProcessSample(
                name=name,
                cpu=cpu,
                command_line=command_line,
                parent_pid=parent_pid,
            )
            children_by_parent.setdefault(parent_pid, []).append(pid)
            if self._is_codex_root(name, command_line):
                roots.append(pid)

        root_pid: int | None = None
        root_cpu_delta = 0.0
        for pid in roots:
            current = next_snapshot[pid]
            previous = self.last_snapshot.get(pid)
            delta = max(current.cpu - previous.cpu, 0.0) if previous is not None else 0.0
            if delta > root_cpu_delta:
                root_cpu_delta = delta
                root_pid = pid

        seen: set[int] = set()
        queue = list(roots)
        while queue:
            current_pid = queue.pop(0)
            if current_pid in seen:
                continue
            seen.add(current_pid)
            queue.extend(children_by_parent.get(current_pid, ()))

        descendants = 0
        hot_descendants = 0
        new_descendants = 0
        build_descendants = 0
        best_score = -1.0
        best_hint = ""
        best_kind = "-"
        best_name = ""
        best_command = ""
        best_pid: int | None = None
        best_reason = "quiet"

        for pid in seen:
            if pid in roots:
                continue
            current = next_snapshot[pid]
            stem = self._process_stem(current.name)
            if self._ignore_codex_child(stem, current.command_line):
                continue

            descendants += 1
            hint = self._hint_from_process(stem, current.command_line)
            kind = self._classify_process_kind(stem, current.command_line, hint)
            if kind == "build":
                build_descendants += 1
            previous = self.last_snapshot.get(pid)
            cpu_delta = max(current.cpu - previous.cpu, 0.0) if previous is not None else 0.0
            is_new = previous is None
            is_hot = is_new or cpu_delta >= ACTIVE_CPU_THRESHOLD
            if is_new:
                new_descendants += 1
            if is_hot:
                hot_descendants += 1

            score = cpu_delta
            if is_new:
                score += NEW_PROCESS_BONUS
            if kind == "build":
                score += 0.02
            if stem in SHELL_STEMS and hint != stem:
                score += 0.01

            if score > best_score:
                best_score = score
                best_hint = hint
                best_kind = kind
                best_name = current.name
                best_command = current.command_line
                best_pid = pid
                if is_new:
                    best_reason = f"new {current.name}"
                elif cpu_delta > 0.0:
                    best_reason = f"{current.name} cpu +{cpu_delta:.3f}"
                else:
                    best_reason = f"{current.name} present"

        self.last_snapshot = next_snapshot

        if descendants == 0 and root_cpu_delta > 0.0:
            best_reason = f"app-server cpu +{root_cpu_delta:.3f}"
        elif descendants == 0 and not roots:
            best_reason = "no app-server"

        return ActivitySnapshot(
            descendants=descendants,
            hot_descendants=hot_descendants,
            new_descendants=new_descendants,
            root_pid=root_pid,
            root_cpu_delta=root_cpu_delta,
            hint=best_hint,
            phase_kind="build" if build_descendants else best_kind,
            source_pid=best_pid,
            source_name=best_name,
            source_command=best_command,
            reason=best_reason,
        )

    def _format_source(self, sample: ActivitySnapshot) -> str:
        if not sample.source_name:
            return self.last_active_source
        stem = self._process_stem(sample.source_name)
        if sample.hint and sample.hint != stem:
            return f"{sample.source_name} [{sample.hint}]"
        return sample.source_name

    def _derive_state(self, sample: ActivitySnapshot, now: float) -> tuple[str, str, str]:
        root_hot = sample.root_cpu_delta >= ROOT_THINKING_CPU_THRESHOLD

        if sample.descendants:
            self.root_activity_streak = 0
        elif root_hot:
            self.last_root_activity_at = now
            self.root_activity_streak = min(self.root_activity_streak + 1, ROOT_THINKING_MIN_STREAK + 2)
        elif now - self.last_root_activity_at >= THINKING_HOLD_SECONDS:
            self.root_activity_streak = 0

        if sample.descendants:
            self.last_descendant_seen_at = now
            if self.last_tool_activity_at <= 0.0:
                self.last_tool_activity_at = now
        if sample.hot_descendants or sample.new_descendants:
            self.last_tool_activity_at = now
        if sample.source_name:
            self.last_active_source = self._format_source(sample)

        quiet_for = now - self.last_tool_activity_at if self.last_tool_activity_at > 0.0 else 999.0
        root_recent = (
            not sample.descendants
            and self.root_activity_streak >= ROOT_THINKING_MIN_STREAK
            and now - self.last_root_activity_at < THINKING_HOLD_SECONDS
        )
        had_active_visual = self.visual_state in ACTIVE_VISUAL_STATES
        state = "idle"
        hint = sample.hint
        reason = sample.reason

        if sample.descendants:
            if sample.phase_kind == "build" and quiet_for < WAITING_GRACE_SECONDS:
                state = "building"
            elif sample.hot_descendants or sample.new_descendants:
                state = "tooling"
            elif quiet_for >= WAITING_GRACE_SECONDS:
                state = "waiting"
            else:
                state = "tooling"
        elif root_recent:
            state = "thinking"
            hint = ""
            reason = f"sustained app-server cpu ({self.root_activity_streak} polls)"

        if state in ACTIVE_VISUAL_STATES:
            self.delivered_until = 0.0
            return state, hint, reason

        if state == "idle" and had_active_visual:
            self.delivered_until = now + DELIVERED_HOLD_SECONDS
            return "delivered", "", "recent work finished"

        if state == "idle" and self.delivered_until > now:
            return "delivered", "", "recent work finished"

        return "idle", "", reason

    def _set_visual_state(self, state: str, hint: str, reason: str) -> None:
        changed = state != self.visual_state or hint != self.activity_hint
        previous = self.visual_state
        self.visual_state = state
        self.activity_hint = hint
        self.last_state_reason = reason
        if changed:
            detail = reason
            if hint:
                detail = f"{detail}; {hint}"
            self._log_debug(f"{previous} -> {state}: {detail}")
        self._refresh_debug_view()

    def _apply_poll_result(self, generation: int, sample: ActivitySnapshot, error_text: str) -> None:
        if self.inflight_generation == generation:
            self.inflight_generation = None

        if generation != self.poll_generation:
            if not self.paused:
                self.root.after(0, self._schedule_poll)
            return

        now = time.monotonic()
        self.last_sample = sample
        self.root_pid = sample.root_pid
        self.root_cpu_delta = sample.root_cpu_delta

        if error_text:
            if error_text != self.last_error_text:
                self._log_debug(f"poll error: {error_text}")
            self.last_error_text = error_text
            self.error_until = now + ERROR_HOLD_SECONDS
            self._refresh_debug_view()
        else:
            if self.last_error_text:
                self._log_debug("poll recovered")
            self.last_error_text = ""
            self.error_until = 0.0
            self.last_successful_poll_at = now
            state, hint, reason = self._derive_state(sample, now)
            self._set_visual_state(state, hint, reason)

        self.root.after(POLL_MS, self._schedule_poll)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = CompanionApp()
    app.run()


if __name__ == "__main__":
    main()
