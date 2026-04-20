from __future__ import annotations

from collections import deque
from ctypes import wintypes
from dataclasses import dataclass
from datetime import datetime
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
from urllib.parse import quote
import winreg


SPI_GETWORKAREA = 0x0030
POLL_MS = 550
IDLE_POLL_MS = 900
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
ROOT_THINKING_MIN_STREAK = 3
SETTINGS_FILENAME = "companion_settings.json"
DEBUG_LOG_LIMIT = 16
TRACE_LOG_LIMIT = 6
REASONING_SIGNAL_TAIL_BYTES = 262144
REASONING_SIGNAL_CHECK_INTERVAL = 0.9
REASONING_SIGNAL_HOLD_SECONDS = 8.0
REASONING_SIGNAL_FRESH_SECONDS = 20.0
ROLLOUT_PATH_REUSE_SECONDS = 2.0
THEME_CHECK_INTERVAL = 2.0
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
STATE_CONFIDENCE_GATES = {
    "building": 0.74,
    "tooling": 0.68,
    "waiting": 0.62,
    "thinking": 0.78,
}
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
WINDOWS_THEME_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
WINDOWS_APPS_THEME_VALUE = "AppsUseLightTheme"
HOMEBASE_WORKSPACE = Path.home() / "OneDrive" / "Homebase"
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
THEME_PALETTES = {
    "light": {
        "art_shadow_far": "",
        "art_shadow_near": "#6f7f76",
        "quote_shadow": "#90a096",
        "state_art_colors": STATE_ART_COLORS,
        "state_quote_colors": STATE_QUOTE_COLORS,
        "debug_bg": "#f4f2ea",
        "debug_border": "#b7b09d",
        "debug_text": "#223127",
        "debug_muted": "#5a685f",
        "buddy_bg": "#f6f3eb",
        "buddy_border": "#bdb39c",
        "buddy_title": "#243127",
        "buddy_copy": "#5a665d",
        "buddy_status": "#35443a",
        "card_bg": "#fffdf8",
        "card_hover_bg": "#f0ece1",
        "card_border": "#d2cab5",
        "card_title": "#223127",
        "card_subtitle": "#5d675e",
    },
    "dark": {
        "art_shadow_far": "",
        "art_shadow_near": "#a7c8af",
        "quote_shadow": "#9ebb9d",
        "state_art_colors": STATE_ART_COLORS,
        "state_quote_colors": {
            "boot": "#9ab8d0",
            "idle": "#a7c38e",
            "thinking": "#a5bfd1",
            "tooling": "#d6c57e",
            "building": "#e4b587",
            "waiting": "#adbbdb",
            "delivered": "#a6d3a4",
            "ping": "#d3ab80",
            "paused": "#a7ada8",
            "error": "#e19a8e",
        },
        "debug_bg": "#0b120d",
        "debug_border": "#26362a",
        "debug_text": "#d9ebd4",
        "debug_muted": "#92a896",
        "buddy_bg": "#101713",
        "buddy_border": "#2a3f32",
        "buddy_title": "#e2f0dc",
        "buddy_copy": "#8ea393",
        "buddy_status": "#b7cdb4",
        "card_bg": "#162019",
        "card_hover_bg": "#1d2a21",
        "card_border": "#304536",
        "card_title": "#eef7eb",
        "card_subtitle": "#9aaf9c",
    },
}
CLEAN_FILES_PROMPT = """Work in conservative Homebase file-organization mode.

Goal:
- help me clean up Homebase without breaking anything

Rules:
- treat this as organization, not aggressive cleanup
- do not delete or move anything on doubt
- prefer review staging, exact paths, and rollback-friendly steps
- start by inspecting Homebase and proposing the safest first pass
"""
SAFETY_SCAN_PROMPT = """A Microsoft Defender quick scan has just been requested from the desktop buddy.

Security mode:
- facts, inferences, and unknowns first
- use exact timestamps and full paths
- stay chat-first unless I explicitly approve host actions
- start by helping me review scan context, recent alerts, and anything suspicious near Homebase
"""
PROCESS_SNAPSHOT_COMMAND = (
    "$cpuById = @{}; "
    "Get-Process | ForEach-Object { "
    "$cpuById[[int]$_.Id] = if ($null -eq $_.CPU) { 0.0 } else { [double]$_.CPU } "
    "}; "
    "$items = @(Get-CimInstance Win32_Process | Select-Object "
    "ProcessId, ParentProcessId, Name, CommandLine, "
    "@{Name='CPU';Expression={ if ($cpuById.ContainsKey([int]$_.ProcessId)) { $cpuById[[int]$_.ProcessId] } else { 0.0 } }}); "
    "if ($items.Count -eq 0) { '[]' } else { $items | ConvertTo-Json -Compress }"
)


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
    meaningful_descendants: int = 0
    quiet_descendants: int = 0
    shell_descendants: int = 0
    specific_shell_descendants: int = 0
    build_descendants: int = 0
    active_build_descendants: int = 0
    reasoning_hit: bool = False
    reasoning_age: float = 999.0
    reasoning_source: str = ""
    reasoning_detail: str = ""
    root_pid: int | None = None
    root_cpu_delta: float = 0.0
    hint: str = ""
    phase_kind: str = "-"
    source_pid: int | None = None
    source_name: str = ""
    source_command: str = ""
    reason: str = "quiet"


@dataclass(slots=True)
class ReasoningProbeResult:
    active: bool = False
    age_seconds: float = 999.0
    source: str = ""
    detail: str = ""


@dataclass(slots=True)
class RolloutScanState:
    path: Path | None = None
    offset: int = 0
    pending_fragment: str = ""
    latest_task_started: float = 0.0
    latest_reasoning: float = 0.0
    latest_assistant: float = 0.0


@dataclass(slots=True)
class SensorDecision:
    chosen_state: str
    candidate_state: str
    candidate_score: float
    hint: str
    reason: str
    rejected: tuple[str, ...] = ()


@dataclass(slots=True)
class SensorTraceEntry:
    chosen_state: str
    candidate_state: str
    root_cpu_delta: float
    descendants: int
    meaningful_descendants: int
    build_descendants: int
    reasoning_hit: bool
    reasoning_age: float
    hint: str
    source: str
    rejected: tuple[str, ...] = ()


def windows_apps_theme_mode() -> str:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WINDOWS_THEME_REG_PATH) as key:
            value, _ = winreg.QueryValueEx(key, WINDOWS_APPS_THEME_VALUE)
    except OSError:
        return "light"
    return "light" if int(value) else "dark"


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
        self.theme_mode = windows_apps_theme_mode()
        self.theme_palette = THEME_PALETTES[self.theme_mode]
        self.last_theme_check_at = 0.0

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
        self.buddy_visible = bool(self._buddy_settings().get("visible", True))
        self.text_visible = bool(self._text_settings().get("visible", True))
        self._start_time = time.monotonic()
        self.codex_home = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
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
        self.live_rollout_path: Path | None = None
        self.last_reasoning_probe_at = 0.0
        self.last_reasoning_probe = ReasoningProbeResult(detail="not checked")
        self.rollout_scan_state = RolloutScanState()
        self.debug_messages: deque[str] = deque(maxlen=DEBUG_LOG_LIMIT)
        self.sensor_traces: deque[SensorTraceEntry] = deque(maxlen=TRACE_LOG_LIMIT)
        self.hit_rects: list[tuple[int, int, int, int]] = []
        self._wndproc = None
        self._old_wndproc = None
        self._set_window_long_ptr = None
        self._call_window_proc = None
        self._long_ptr_type = None
        self.debug_summary_var = tk.StringVar(master=self.root, value="")
        self.debug_log_var = tk.StringVar(master=self.root, value="")
        self.debug_window: tk.Toplevel | None = None
        self.debug_summary_label: tk.Label | None = None
        self.debug_log_label: tk.Label | None = None
        self.debug_divider: tk.Frame | None = None
        self.debug_summary_cache = ""
        self.debug_log_cache = ""
        self.buddy_window: tk.Toplevel | None = None
        self.buddy_body_frame: tk.Frame | None = None
        self.buddy_state_var = tk.StringVar(master=self.root, value="Pod says syncing.")
        self.buddy_status_var = tk.StringVar(master=self.root, value="Quiet help nearby.")
        self.buddy_cards: list[dict[str, object]] = []
        self.buddy_title_label: tk.Label | None = None
        self.buddy_copy_label: tk.Label | None = None
        self.buddy_state_label: tk.Label | None = None
        self.buddy_status_label: tk.Label | None = None
        self.display_layout_cache: dict[
            tuple[str, str, str],
            tuple[int, int, int, int, int, tuple[tuple[int, int, int, int], ...]],
        ] = {}

        self._build_ui()
        self._bind_events()
        self._install_hit_test_hook()
        self._restore_saved_geometry()
        if self.buddy_visible:
            self._ensure_buddy_window()
            self.root.after(120, self._place_buddy_window)
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
            "buddy": {
                "visible": True,
            },
            "text": {
                "visible": True,
            },
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

        buddy_payload = payload.get("buddy")
        if isinstance(buddy_payload, dict):
            buddy_settings = settings["buddy"]
            if isinstance(buddy_payload.get("visible"), bool):
                buddy_settings["visible"] = buddy_payload["visible"]

        text_payload = payload.get("text")
        if isinstance(text_payload, dict):
            text_settings = settings["text"]
            if isinstance(text_payload.get("visible"), bool):
                text_settings["visible"] = text_payload["visible"]

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

    def _buddy_settings(self) -> dict[str, object]:
        buddy_settings = self.settings.get("buddy")
        if isinstance(buddy_settings, dict):
            return buddy_settings
        buddy_settings = {"visible": True}
        self.settings["buddy"] = buddy_settings
        return buddy_settings

    def _text_settings(self) -> dict[str, object]:
        text_settings = self.settings.get("text")
        if isinstance(text_settings, dict):
            return text_settings
        text_settings = {"visible": True}
        self.settings["text"] = text_settings
        return text_settings

    def _save_settings(self) -> None:
        window_settings = self._window_settings()
        window_settings["docked"] = self.docked
        if self.root.winfo_exists():
            window_settings["x"] = int(self.root.winfo_x())
            window_settings["y"] = int(self.root.winfo_y())
        self.settings["debug"] = self.debug_visible
        self._buddy_settings()["visible"] = self.buddy_visible
        self._text_settings()["visible"] = self.text_visible
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
        self._place_aux_windows()

    def _remember_window_position(self, *, docked: bool | None = None) -> None:
        if docked is not None:
            self.docked = docked
        self._save_settings()
        self._place_aux_windows()

    def _build_ui(self) -> None:
        self.art_font = tkfont.Font(family="Consolas", size=9, weight="bold")
        self.quote_font = tkfont.Font(family="Consolas", size=7)
        self.debug_font = tkfont.Font(family="Consolas", size=8)
        self.buddy_title_font = tkfont.Font(family="Segoe UI Semibold", size=10)
        self.buddy_body_font = tkfont.Font(family="Segoe UI", size=8)
        self.buddy_state_font = tkfont.Font(family="Consolas", size=8)
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
            fill=self.theme_palette["art_shadow_far"],
            font=self.art_font,
            anchor="nw",
            justify="left",
        )
        self.shadow_near_item = self.canvas.create_text(
            1,
            1,
            text=initial_art,
            fill=self.theme_palette["art_shadow_near"],
            font=self.art_font,
            anchor="nw",
            justify="left",
        )
        self.art_item = self.canvas.create_text(
            0,
            0,
            text=initial_art,
            fill=self.theme_palette["state_art_colors"]["boot"],
            font=self.art_font,
            anchor="nw",
            justify="left",
        )
        self.quote_shadow_item = self.canvas.create_text(
            1,
            height + 4,
            text=STATE_QUOTES["boot"],
            fill=self.theme_palette["quote_shadow"],
            font=self.quote_font,
            anchor="nw",
            justify="left",
        )
        self.quote_item = self.canvas.create_text(
            0,
            height + 3,
            text=STATE_QUOTES["boot"],
            fill=self.theme_palette["state_quote_colors"]["boot"],
            font=self.quote_font,
            anchor="nw",
            justify="left",
        )
        self.canvas.pack(anchor="w", padx=1, pady=1)
        self._set_display("boot", initial_art)

        self.menu = tk.Menu(self.root, tearoff=False)
        self.menu.add_command(label="Hide Menu", command=self._toggle_buddy_window)
        self.buddy_menu_index = 0
        self.menu.add_command(label="Hide Text", command=self._toggle_text)
        self.text_menu_index = 1
        self.menu.add_command(label="Redock Above Clock", command=self._dock_above_clock)
        self.menu.add_command(label="Pause Sensing", command=self._toggle_pause)
        self.pause_menu_index = 3
        self.menu.add_command(label="Show Diagnostics", command=self._toggle_debug_window)
        self.debug_menu_index = 4
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
        self._place_aux_windows()

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
        self.menu.entryconfigure(self.buddy_menu_index, label="Hide Menu" if self.buddy_visible else "Show Menu")
        self.menu.entryconfigure(self.text_menu_index, label="Hide Text" if self.text_visible else "Show Text")
        self.menu.entryconfigure(self.pause_menu_index, label="Resume Sensing" if self.paused else "Pause Sensing")
        self.menu.entryconfigure(self.debug_menu_index, label="Hide Diagnostics" if self.debug_visible else "Show Diagnostics")

    def _reset_reasoning_probe_state(self, detail: str) -> None:
        self.live_rollout_path = None
        self.last_reasoning_probe_at = 0.0
        self.last_reasoning_probe = ReasoningProbeResult(detail=detail)
        self.rollout_scan_state = RolloutScanState()

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
            self._place_aux_windows()

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
        self._reset_reasoning_probe_state("paused")
        self.sensor_traces.clear()
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

    def _toggle_buddy_window(self) -> None:
        if self.buddy_visible:
            self._hide_buddy_window()
            return
        self.buddy_visible = True
        self._ensure_buddy_window()
        self._save_settings()
        self._update_menu_labels()
        self._log_debug("desktop buddy shown")

    def _toggle_text(self) -> None:
        self.text_visible = not self.text_visible
        self._save_settings()
        self._update_menu_labels()
        current_state = self._current_state()
        art = self.canvas.itemcget(self.art_item, "text") or self._frames_for_state(current_state)[0]
        self._set_display(current_state, art)
        self._log_debug("pod text shown" if self.text_visible else "pod text hidden")

    def _ensure_debug_window(self) -> None:
        if self.debug_window is not None and self.debug_window.winfo_exists():
            self._place_debug_window()
            self._refresh_debug_view(force=True)
            return

        self.debug_window = tk.Toplevel(self.root)
        self.debug_window.title("Courier Diagnostics")
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

        self.debug_summary_label = tk.Label(
            self.debug_window,
            textvariable=self.debug_summary_var,
            font=self.debug_font,
            justify="left",
            anchor="nw",
        )
        self.debug_summary_label.pack(fill="both", expand=False, padx=10, pady=(10, 6))

        self.debug_divider = tk.Frame(self.debug_window, height=1, bd=0, highlightthickness=0)
        self.debug_divider.pack(fill="x", padx=10, pady=(0, 6))

        self.debug_log_label = tk.Label(
            self.debug_window,
            textvariable=self.debug_log_var,
            font=self.debug_font,
            justify="left",
            anchor="nw",
        )
        self.debug_log_label.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.debug_window.protocol("WM_DELETE_WINDOW", self._hide_debug_window)
        self._apply_debug_theme()
        self._place_debug_window()
        self._refresh_debug_view(force=True)

    def _hide_debug_window(self) -> None:
        self.debug_visible = False
        if self.debug_window is not None and self.debug_window.winfo_exists():
            self.debug_window.destroy()
        self.debug_window = None
        self._save_settings()
        self._update_menu_labels()
        self._refresh_debug_view()

    def _ensure_buddy_window(self) -> None:
        if self.buddy_window is not None and self.buddy_window.winfo_exists():
            self._place_buddy_window()
            self._refresh_buddy_labels()
            return

        self.buddy_window = tk.Toplevel(self.root)
        self.buddy_window.title("Desktop Buddy")
        self.buddy_window.resizable(False, False)
        self.buddy_window.attributes("-topmost", True)
        try:
            self.buddy_window.wm_attributes("-toolwindow", True)
        except tk.TclError:
            pass
        try:
            self.buddy_window.wm_attributes("-alpha", 0.97)
        except tk.TclError:
            pass

        self.buddy_body_frame = tk.Frame(self.buddy_window, bd=0, highlightthickness=0)
        self.buddy_body_frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.buddy_title_label = tk.Label(
            self.buddy_body_frame,
            text="Pocket menu",
            font=self.buddy_title_font,
            anchor="w",
            justify="left",
        )
        self.buddy_title_label.pack(fill="x")

        self.buddy_copy_label = tk.Label(
            self.buddy_body_frame,
            text="A small field kit for cleanup, scan-ups, and fast handoffs.",
            font=self.buddy_body_font,
            anchor="w",
            justify="left",
            wraplength=248,
        )
        self.buddy_copy_label.pack(fill="x", pady=(4, 8))

        self.buddy_state_label = tk.Label(
            self.buddy_body_frame,
            textvariable=self.buddy_state_var,
            font=self.buddy_state_font,
            anchor="w",
            justify="left",
        )
        self.buddy_state_label.pack(fill="x", pady=(0, 10))

        self.buddy_cards = []
        self._add_buddy_card(
            self.buddy_body_frame,
            title="Clean files",
            subtitle="Open a conservative Homebase cleanup thread. No blind deletes.",
            accent="#87c76e",
            command=self._launch_clean_files_flow,
        )
        self._add_buddy_card(
            self.buddy_body_frame,
            title="Safety scan",
            subtitle="Request Defender quick scan and open a triage thread in parallel.",
            accent="#d7b16d",
            command=self._launch_safety_scan_flow,
        )

        self.buddy_status_label = tk.Label(
            self.buddy_body_frame,
            textvariable=self.buddy_status_var,
            font=self.buddy_body_font,
            anchor="w",
            justify="left",
            wraplength=248,
        )
        self.buddy_status_label.pack(fill="x", pady=(10, 0))

        self.buddy_window.protocol("WM_DELETE_WINDOW", self._hide_buddy_window)
        self._apply_buddy_theme()
        self._place_buddy_window()
        self._refresh_buddy_labels()

    def _hide_buddy_window(self) -> None:
        self.buddy_visible = False
        if self.buddy_window is not None and self.buddy_window.winfo_exists():
            self.buddy_window.destroy()
        self.buddy_window = None
        self.buddy_body_frame = None
        self.buddy_cards = []
        self._save_settings()
        self._update_menu_labels()
        self._log_debug("desktop buddy hidden")

    def _add_buddy_card(
        self,
        parent: tk.Misc,
        *,
        title: str,
        subtitle: str,
        accent: str,
        command: object,
    ) -> None:
        card = tk.Frame(parent, bd=0, highlightthickness=1, cursor="hand2")
        accent_bar = tk.Frame(card, width=4, bg=accent, bd=0, highlightthickness=0)
        accent_bar.pack(side="left", fill="y")

        text_frame = tk.Frame(card, bd=0, highlightthickness=0)
        text_frame.pack(side="left", fill="both", expand=True, padx=(10, 12), pady=9)

        title_label = tk.Label(
            text_frame,
            text=title,
            font=self.buddy_title_font,
            anchor="w",
            justify="left",
        )
        title_label.pack(fill="x")

        subtitle_label = tk.Label(
            text_frame,
            text=subtitle,
            font=self.buddy_body_font,
            anchor="w",
            justify="left",
            wraplength=212,
        )
        subtitle_label.pack(fill="x", pady=(2, 0))

        card_info = {
            "frame": card,
            "text_frame": text_frame,
            "title": title_label,
            "subtitle": subtitle_label,
            "accent_bar": accent_bar,
            "accent": accent,
            "command": command,
            "hovered": False,
        }
        self.buddy_cards.append(card_info)
        for widget in (card, text_frame, title_label, subtitle_label, accent_bar):
            widget.bind("<Enter>", lambda _event, info=card_info: self._set_buddy_card_hover(info, True))
            widget.bind("<Leave>", lambda _event, info=card_info: self._set_buddy_card_hover(info, False))
            widget.bind("<Button-1>", lambda _event, info=card_info: self._run_buddy_card(info))
        card.pack(fill="x", pady=(0, 8))
        self._set_buddy_card_hover(card_info, False)

    def _run_buddy_card(self, card_info: dict[str, object]) -> None:
        self.nudge_until = time.monotonic() + PING_SECONDS
        command = card_info.get("command")
        if callable(command):
            command()

    def _set_buddy_card_hover(self, card_info: dict[str, object], hovered: bool) -> None:
        card_info["hovered"] = hovered
        palette = self.theme_palette
        bg = palette["card_hover_bg"] if hovered else palette["card_bg"]
        border = card_info.get("accent") if hovered else palette["card_border"]
        for key in ("frame", "text_frame", "title", "subtitle"):
            widget = card_info.get(key)
            if isinstance(widget, tk.Misc):
                widget.configure(bg=bg)
        frame = card_info.get("frame")
        if isinstance(frame, tk.Frame):
            frame.configure(highlightbackground=border, highlightcolor=border)
        title = card_info.get("title")
        if isinstance(title, tk.Label):
            title.configure(fg=palette["card_title"])
        subtitle = card_info.get("subtitle")
        if isinstance(subtitle, tk.Label):
            subtitle.configure(fg=palette["card_subtitle"])

    def _refresh_buddy_labels(self) -> None:
        state = self._current_state()
        phrase = self._quote_for_state(state) or STATE_QUOTES.get(state, state)
        self.buddy_state_var.set(f"Pod says {phrase}.")

    def _set_buddy_status(self, message: str) -> None:
        self.buddy_status_var.set(message)
        if self.buddy_window is not None and self.buddy_window.winfo_exists():
            self.buddy_window.update_idletasks()

    def _default_workspace(self, preferred: Path) -> Path:
        if preferred.exists():
            return preferred
        return Path.home()

    def _launch_codex_thread(self, prompt: str, workspace: Path) -> tuple[bool, str]:
        target = self._default_workspace(workspace)
        codex_url = f"codex://new?prompt={quote(prompt, safe='')}&path={quote(str(target), safe='')}"
        try:
            os.startfile(codex_url)
        except OSError as exc:
            return False, str(exc)
        return True, str(target)

    def _launch_defender_quick_scan(self) -> tuple[bool, str]:
        scan_command = "try { Start-MpScan -ScanType QuickScan } catch { exit 1 }"
        try:
            subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-WindowStyle",
                    "Hidden",
                    "-Command",
                    scan_command,
                ],
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError as exc:
            return False, str(exc)
        return True, "Defender quick scan requested."

    def _launch_clean_files_flow(self) -> None:
        ok, detail = self._launch_codex_thread(CLEAN_FILES_PROMPT, HOMEBASE_WORKSPACE)
        if ok:
            self._set_buddy_status("Opened a conservative Homebase cleanup thread.")
            self._log_debug("desktop buddy opened clean-files flow")
            return
        self._set_buddy_status(f"Clean-files launch failed: {detail}")
        self._log_debug(f"desktop buddy clean-files failed: {detail}")

    def _launch_safety_scan_flow(self) -> None:
        thread_ok, thread_detail = self._launch_codex_thread(SAFETY_SCAN_PROMPT, HOMEBASE_WORKSPACE)
        scan_ok, scan_detail = self._launch_defender_quick_scan()
        if thread_ok and scan_ok:
            self._set_buddy_status("Safety scan requested. Defender is running in the background.")
            self._log_debug("desktop buddy launched safety scan")
            return
        problems = []
        if not scan_ok:
            problems.append(f"scan: {scan_detail}")
        if not thread_ok:
            problems.append(f"thread: {thread_detail}")
        detail = "; ".join(problems) if problems else "unknown launch issue"
        self._set_buddy_status(f"Safety scan launch failed: {detail}")
        self._log_debug(f"desktop buddy safety-scan failed: {detail}")

    def _place_aux_windows(self) -> None:
        self._place_buddy_window()
        self._place_debug_window()

    def _apply_debug_theme(self) -> None:
        if self.debug_window is None or not self.debug_window.winfo_exists():
            return
        palette = self.theme_palette
        self.debug_window.configure(
            bg=palette["debug_bg"],
            highlightbackground=palette["debug_border"],
            highlightcolor=palette["debug_border"],
            highlightthickness=1,
        )
        if self.debug_summary_label is not None:
            self.debug_summary_label.configure(bg=palette["debug_bg"], fg=palette["debug_text"])
        if self.debug_log_label is not None:
            self.debug_log_label.configure(bg=palette["debug_bg"], fg=palette["debug_muted"])
        if self.debug_divider is not None:
            self.debug_divider.configure(bg=palette["debug_border"])

    def _apply_buddy_theme(self) -> None:
        if self.buddy_window is None or not self.buddy_window.winfo_exists():
            return
        palette = self.theme_palette
        self.buddy_window.configure(
            bg=palette["buddy_bg"],
            highlightbackground=palette["buddy_border"],
            highlightcolor=palette["buddy_border"],
            highlightthickness=1,
        )
        if self.buddy_body_frame is not None:
            self.buddy_body_frame.configure(bg=palette["buddy_bg"])
        for widget, fg_key in (
            (self.buddy_title_label, "buddy_title"),
            (self.buddy_copy_label, "buddy_copy"),
            (self.buddy_state_label, "buddy_status"),
            (self.buddy_status_label, "buddy_status"),
        ):
            if widget is not None:
                widget.configure(bg=palette["buddy_bg"], fg=palette[fg_key])
        for card_info in self.buddy_cards:
            self._set_buddy_card_hover(card_info, bool(card_info.get("hovered")))

    def _refresh_theme(self, *, force: bool = False) -> None:
        now = time.monotonic()
        if not force and now - self.last_theme_check_at < THEME_CHECK_INTERVAL:
            return
        self.last_theme_check_at = now
        theme_mode = windows_apps_theme_mode()
        if not force and theme_mode == self.theme_mode:
            return
        self.theme_mode = theme_mode
        self.theme_palette = THEME_PALETTES[theme_mode]
        self._apply_debug_theme()
        self._apply_buddy_theme()
        if hasattr(self, "canvas"):
            current_state = self._current_state()
            art = self.canvas.itemcget(self.art_item, "text") or self._frames_for_state(current_state)[0]
            self._set_display(current_state, art)
        self._log_debug(f"theme -> {theme_mode}")

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

    def _place_buddy_window(self) -> None:
        if self.buddy_window is None or not self.buddy_window.winfo_exists():
            return
        self.root.update_idletasks()
        self.buddy_window.update_idletasks()
        width = self.buddy_window.winfo_reqwidth()
        height = self.buddy_window.winfo_reqheight()
        x = self.root.winfo_x() + self.root.winfo_width() - width
        y = self.root.winfo_y() - height - 16
        area = windows_work_area()
        if area is not None:
            left, top, right, bottom = area
            if y < top + 8:
                y = min(self.root.winfo_y() + self.root.winfo_height() + 14, bottom - height - 8)
            x = min(max(x, left + 8), max(left + 8, right - width - 8))
            y = min(max(y, top + 8), max(top + 8, bottom - height - 8))
        self.buddy_window.geometry(f"+{x}+{y}")

    def _age_text(self, timestamp: float) -> str:
        if timestamp <= 0.0:
            return "-"
        return f"{max(time.monotonic() - timestamp, 0.0):.1f}s"

    def _reasoning_debug_text(self, sample: ActivitySnapshot) -> str:
        if sample.reasoning_hit:
            source = sample.reasoning_source or "rollout"
            return f"{source} {sample.reasoning_age:.1f}s ago"
        if sample.reasoning_detail:
            return sample.reasoning_detail
        return "-"

    def _refresh_debug_view(self, *, force: bool = False) -> None:
        window_live = self.debug_window is not None and self.debug_window.winfo_exists()
        if not force and (not self.debug_visible or not window_live):
            return
        summary_lines = [
            f"state      {self._current_state()}",
            f"hint       {self.activity_hint or '-'}",
            f"reason     {self.last_state_reason or '-'}",
            f"source     {self.last_active_source or '-'}",
            f"poll gen   {self.poll_generation} / {self.inflight_generation if self.inflight_generation is not None else '-'}",
            f"root cpu   {self.root_cpu_delta:.3f} (pid {self.root_pid or '-'})",
            f"root gate  {self.root_activity_streak}/{ROOT_THINKING_MIN_STREAK} over {ROOT_THINKING_CPU_THRESHOLD:.3f}",
            (
                f"desc       {self.last_sample.descendants} total, "
                f"{self.last_sample.meaningful_descendants} meaningful, "
                f"{self.last_sample.hot_descendants} hot, {self.last_sample.new_descendants} new"
            ),
            (
                f"class      {self.last_sample.shell_descendants} shell, "
                f"{self.last_sample.build_descendants} build, "
                f"{self.last_sample.quiet_descendants} quiet"
            ),
            f"kind       {self.last_sample.phase_kind or '-'}",
            (
                f"reasoning  {'hit' if self.last_sample.reasoning_hit else 'miss'} "
                f"{self._reasoning_debug_text(self.last_sample)}"
            ),
            f"last poll  {self._age_text(self.last_successful_poll_at)} ago",
            f"error      {self.last_error_text or '-'}",
        ]
        summary_text = "\n".join(summary_lines)
        trace_lines = self._sensor_trace_lines()
        event_lines = list(self.debug_messages)[-6:]
        blocks: list[str] = []
        if trace_lines:
            blocks.extend(["sensor trace", *trace_lines])
        if event_lines:
            if blocks:
                blocks.append("")
            blocks.extend(["events", *event_lines])
        log_text = "\n".join(blocks) if blocks else "no diagnostics yet"
        if summary_text != self.debug_summary_cache:
            self.debug_summary_cache = summary_text
            self.debug_summary_var.set(summary_text)
        if log_text != self.debug_log_cache:
            self.debug_log_cache = log_text
            self.debug_log_var.set(log_text)

    def _log_debug(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.debug_messages.append(f"{timestamp} {message}")
        self._refresh_debug_view()

    def _sensor_trace_lines(self) -> list[str]:
        lines: list[str] = []
        for entry in self.sensor_traces:
            signal = entry.source or entry.hint or "-"
            reasoning = f"yes@{entry.reasoning_age:.1f}s" if entry.reasoning_hit else "no"
            lines.append(
                (
                    f"{entry.chosen_state:<9} cand {entry.candidate_state:<8} "
                    f"root {entry.root_cpu_delta:.3f} desc {entry.meaningful_descendants}/{entry.descendants} "
                    f"build {entry.build_descendants} think {reasoning:<8} sig {signal}"
                )
            )
            if entry.rejected:
                lines.append(f"  no       {' | '.join(entry.rejected[:3])}")
        return lines

    def _record_sensor_trace(self, sample: ActivitySnapshot, decision: SensorDecision) -> None:
        self.sensor_traces.appendleft(
            SensorTraceEntry(
                chosen_state=decision.chosen_state,
                candidate_state=decision.candidate_state,
                root_cpu_delta=sample.root_cpu_delta,
                descendants=sample.descendants,
                meaningful_descendants=sample.meaningful_descendants,
                build_descendants=sample.build_descendants,
                reasoning_hit=sample.reasoning_hit,
                reasoning_age=sample.reasoning_age,
                hint=sample.hint,
                source=self._format_source(sample) if sample.source_name else "",
                rejected=decision.rejected,
            )
        )

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
        if self.visual_state == "boot":
            if now < self.start_time + BOOT_SECONDS:
                return "boot"
            return "idle"
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
        if not self.text_visible:
            return ""
        if state == "tooling":
            return self._tooling_quote()
        if state == "building":
            return self._building_quote()
        if state in {"thinking", "waiting"}:
            return ""
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

    def _compute_hit_rects(self, art: str, quote: str, art_x: int, quote_x: int, quote_y: int) -> tuple[tuple[int, int, int, int], ...]:
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
        return tuple(rects)

    def _set_display(self, state: str, art: str) -> None:
        quote = self._quote_for_state(state)
        pad_x = 2
        pad_y = 2
        palette = self.theme_palette
        layout_key = (state, art, quote)
        layout = self.display_layout_cache.get(layout_key)
        if layout is None:
            art_width, art_height = self._measure_text(art, self.art_font)
            quote_width, quote_height = self._measure_text(quote, self.quote_font) if quote else (0, 0)
            content_width = max(art_width, quote_width)
            content_height = art_height + (quote_height + 4 if quote else 0)
            art_x = pad_x + (content_width - art_width) // 2
            quote_x = pad_x + (content_width - quote_width) // 2 if quote else pad_x
            quote_y = pad_y + art_height + 3
            hit_rects = self._compute_hit_rects(art, quote, art_x, quote_x, quote_y)
            layout = (content_width, content_height, art_x, quote_x, quote_y, hit_rects)
            self.display_layout_cache[layout_key] = layout
        content_width, content_height, art_x, quote_x, quote_y, hit_rects = layout
        self.canvas.configure(width=content_width + 4, height=content_height + 4)
        far_shadow = palette["art_shadow_far"]
        self.canvas.itemconfigure(self.shadow_far_item, text=art if far_shadow else "", fill=far_shadow)
        self.canvas.itemconfigure(self.shadow_near_item, text=art, fill=palette["art_shadow_near"])
        self.canvas.itemconfigure(self.art_item, text=art, fill=palette["state_art_colors"][state])
        self.canvas.coords(self.shadow_far_item, art_x - 1, pad_y)
        self.canvas.coords(self.shadow_near_item, art_x + 1, pad_y + 1)
        self.canvas.coords(self.art_item, art_x, pad_y)
        self.canvas.itemconfigure(self.quote_shadow_item, text=quote, fill=palette["quote_shadow"])
        self.canvas.itemconfigure(self.quote_item, text=quote, fill=palette["state_quote_colors"][state])
        self.canvas.coords(self.quote_shadow_item, quote_x + 1, quote_y + 1)
        self.canvas.coords(self.quote_item, quote_x, quote_y)
        self.hit_rects = list(hit_rects)
        self._refresh_buddy_labels()

    def _animate(self) -> None:
        self._refresh_theme()
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
        try:
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", PROCESS_SNAPSHOT_COMMAND],
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

    def _next_poll_delay_ms(self, sample: ActivitySnapshot | None, error_text: str) -> int:
        if error_text:
            return POLL_MS
        if sample is None:
            return POLL_MS
        if sample.root_pid or sample.descendants or sample.reasoning_hit:
            return POLL_MS
        return IDLE_POLL_MS

    def _normalize_snapshot(self, payload: str) -> list[dict[str, object]]:
        if not payload:
            return []
        data = json.loads(payload)
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        return []

    def _parse_event_timestamp(self, raw: object) -> float:
        if not isinstance(raw, str) or not raw:
            return 0.0
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return 0.0

    def _locate_live_rollout_path(self, now_epoch: float) -> Path | None:
        if self.live_rollout_path is not None:
            try:
                modified = self.live_rollout_path.stat().st_mtime
            except OSError:
                self.live_rollout_path = None
            else:
                if now_epoch - modified <= ROLLOUT_PATH_REUSE_SECONDS:
                    return self.live_rollout_path
        sessions_root = self.codex_home / "sessions"
        best_path: Path | None = None
        best_mtime = 0.0
        for day_offset in (0, 1):
            day = time.localtime(now_epoch - (day_offset * 86400))
            day_dir = sessions_root / f"{day.tm_year:04d}" / f"{day.tm_mon:02d}" / f"{day.tm_mday:02d}"
            if not day_dir.exists():
                continue
            try:
                for child in day_dir.iterdir():
                    if child.suffix != ".jsonl" or not child.is_file():
                        continue
                    try:
                        modified = child.stat().st_mtime
                    except OSError:
                        continue
                    if modified > best_mtime and now_epoch - modified <= REASONING_SIGNAL_FRESH_SECONDS:
                        best_mtime = modified
                        best_path = child
            except OSError:
                continue
        self.live_rollout_path = best_path
        return best_path

    def _read_rollout_lines(self, path: Path) -> list[str] | None:
        state = self.rollout_scan_state
        try:
            size = path.stat().st_size
        except OSError:
            return None

        reset_scan = state.path != path or size < state.offset
        start = max(size - REASONING_SIGNAL_TAIL_BYTES, 0) if reset_scan else state.offset
        try:
            with path.open("rb") as handle:
                prefix = b""
                if reset_scan and start > 0:
                    handle.seek(start - 1)
                    prefix = handle.read(1)
                handle.seek(start)
                chunk = handle.read()
        except OSError:
            return None

        text = chunk.decode("utf-8", errors="ignore")
        if reset_scan:
            state = RolloutScanState(path=path, offset=size)
            if start > 0 and prefix not in {b"\n", b"\r"}:
                newline_index = text.find("\n")
                if newline_index == -1:
                    self.rollout_scan_state = state
                    return []
                text = text[newline_index + 1 :]
        else:
            state.offset = size
            if state.pending_fragment:
                text = state.pending_fragment + text
                state.pending_fragment = ""

        lines = text.splitlines()
        if text and not text.endswith(("\n", "\r")):
            state.pending_fragment = lines.pop() if lines else text
        else:
            state.pending_fragment = ""

        self.rollout_scan_state = state
        return lines

    def _rollout_probe_timestamps(self, path: Path) -> tuple[float, float, float] | None:
        lines = self._read_rollout_lines(path)
        if lines is None:
            return None

        state = self.rollout_scan_state
        for line in lines:
            if '"timestamp"' not in line:
                continue
            if (
                '"task_started"' not in line
                and '"payload":{"type":"reasoning"' not in line
                and '"role":"assistant"' not in line
            ):
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            timestamp = self._parse_event_timestamp(item.get("timestamp"))
            if timestamp <= 0.0:
                continue
            payload = item.get("payload")
            if not isinstance(payload, dict):
                continue
            if item.get("type") == "event_msg" and payload.get("type") == "task_started":
                state.latest_task_started = max(state.latest_task_started, timestamp)
                continue
            if item.get("type") != "response_item":
                continue
            if payload.get("type") == "reasoning":
                state.latest_reasoning = max(state.latest_reasoning, timestamp)
                continue
            if payload.get("type") == "message" and payload.get("role") == "assistant":
                state.latest_assistant = max(state.latest_assistant, timestamp)

        return state.latest_task_started, state.latest_reasoning, state.latest_assistant

    def _scan_reasoning_probe(self) -> ReasoningProbeResult:
        now = time.monotonic()
        if now - self.last_reasoning_probe_at < REASONING_SIGNAL_CHECK_INTERVAL:
            return self.last_reasoning_probe
        self.last_reasoning_probe_at = now

        now_epoch = time.time()
        rollout_path = self._locate_live_rollout_path(now_epoch)
        if rollout_path is None:
            self.last_reasoning_probe = ReasoningProbeResult(detail="no live rollout")
            return self.last_reasoning_probe

        timestamps = self._rollout_probe_timestamps(rollout_path)
        if timestamps is None:
            self.last_reasoning_probe = ReasoningProbeResult(source=rollout_path.name, detail="rollout unreadable")
            return self.last_reasoning_probe

        latest_task_started, latest_reasoning, latest_assistant = timestamps

        age_seconds = max(now_epoch - latest_reasoning, 0.0) if latest_reasoning else 999.0
        if (
            latest_reasoning
            and latest_reasoning >= latest_task_started
            and latest_assistant < latest_reasoning
            and age_seconds <= REASONING_SIGNAL_HOLD_SECONDS
        ):
            result = ReasoningProbeResult(
                active=True,
                age_seconds=age_seconds,
                source=rollout_path.name,
                detail=f"rollout reasoning {age_seconds:.1f}s ago",
            )
        elif latest_reasoning and latest_assistant >= latest_reasoning:
            result = ReasoningProbeResult(
                age_seconds=age_seconds,
                source=rollout_path.name,
                detail="rollout already answered",
            )
        elif latest_reasoning and latest_reasoning < latest_task_started:
            result = ReasoningProbeResult(
                age_seconds=age_seconds,
                source=rollout_path.name,
                detail="reasoning from earlier turn",
            )
        elif latest_reasoning:
            result = ReasoningProbeResult(
                age_seconds=age_seconds,
                source=rollout_path.name,
                detail=f"rollout reasoning stale {age_seconds:.1f}s",
            )
        else:
            result = ReasoningProbeResult(source=rollout_path.name, detail="no rollout reasoning hit")

        self.last_reasoning_probe = result
        return result

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
        queue = deque(roots)
        while queue:
            current_pid = queue.popleft()
            if current_pid in seen:
                continue
            seen.add(current_pid)
            queue.extend(children_by_parent.get(current_pid, ()))

        descendants = 0
        hot_descendants = 0
        new_descendants = 0
        meaningful_descendants = 0
        quiet_descendants = 0
        shell_descendants = 0
        specific_shell_descendants = 0
        build_descendants = 0
        active_build_descendants = 0
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
            is_shell = stem in SHELL_STEMS
            if is_shell:
                shell_descendants += 1
                if hint != stem:
                    specific_shell_descendants += 1
            if kind == "build":
                build_descendants += 1
            previous = self.last_snapshot.get(pid)
            cpu_delta = max(current.cpu - previous.cpu, 0.0) if previous is not None else 0.0
            is_new = previous is None
            is_hot = cpu_delta >= ACTIVE_CPU_THRESHOLD
            meaningful = is_hot or (is_new and (kind == "build" or hint != stem or not is_shell))
            if is_new:
                new_descendants += 1
            if is_hot:
                hot_descendants += 1
            if meaningful:
                meaningful_descendants += 1
                if kind == "build":
                    active_build_descendants += 1
            else:
                quiet_descendants += 1

            score = cpu_delta
            if meaningful and is_new:
                score += NEW_PROCESS_BONUS
            if meaningful and kind == "build":
                score += 0.02
            if is_shell and hint != stem:
                score += 0.01
            if not meaningful:
                score -= 0.02

            if score > best_score:
                best_score = score
                best_hint = hint
                best_kind = kind
                best_name = current.name
                best_command = current.command_line
                best_pid = pid
                if meaningful and is_new:
                    best_reason = f"new {current.name}"
                elif is_hot:
                    best_reason = f"{current.name} cpu +{cpu_delta:.3f}"
                elif is_shell and hint == stem:
                    best_reason = f"quiet {current.name}"
                else:
                    best_reason = f"{current.name} present"

        self.last_snapshot = next_snapshot

        if descendants == 0 and root_cpu_delta > 0.0:
            best_reason = f"app-server cpu +{root_cpu_delta:.3f}"
        elif descendants == 0 and not roots:
            best_reason = "no app-server"
        elif descendants and meaningful_descendants == 0:
            if shell_descendants == descendants:
                best_reason = "shell presence only"
            else:
                best_reason = "quiet descendants only"

        reasoning = ReasoningProbeResult(detail="child path present" if descendants else "root quiet")
        should_probe_reasoning = (
            not descendants
            and bool(roots)
            and (root_cpu_delta > 0.0 or self.root_activity_streak > 0 or self.last_reasoning_probe.active)
        )
        if should_probe_reasoning:
            reasoning = self._scan_reasoning_probe()
        elif not roots:
            reasoning = ReasoningProbeResult(detail="no app-server")

        return ActivitySnapshot(
            descendants=descendants,
            hot_descendants=hot_descendants,
            new_descendants=new_descendants,
            meaningful_descendants=meaningful_descendants,
            quiet_descendants=quiet_descendants,
            shell_descendants=shell_descendants,
            specific_shell_descendants=specific_shell_descendants,
            build_descendants=build_descendants,
            active_build_descendants=active_build_descendants,
            reasoning_hit=reasoning.active,
            reasoning_age=reasoning.age_seconds,
            reasoning_source=reasoning.source,
            reasoning_detail=reasoning.detail,
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

    def _derive_state(self, sample: ActivitySnapshot, now: float) -> SensorDecision:
        root_hot = sample.root_cpu_delta >= ROOT_THINKING_CPU_THRESHOLD

        if sample.meaningful_descendants:
            self.root_activity_streak = 0
            self.last_descendant_seen_at = now
            self.last_tool_activity_at = now
        else:
            if sample.descendants:
                self.last_descendant_seen_at = now
        if not sample.descendants and root_hot:
            self.last_root_activity_at = now
            self.root_activity_streak = min(self.root_activity_streak + 1, ROOT_THINKING_MIN_STREAK + 3)
        elif now - self.last_root_activity_at >= THINKING_HOLD_SECONDS:
            self.root_activity_streak = 0

        if sample.source_name:
            self.last_active_source = self._format_source(sample)

        quiet_for = now - self.last_tool_activity_at if self.last_tool_activity_at > 0.0 else 999.0
        had_active_visual = self.visual_state in ACTIVE_VISUAL_STATES
        scores: dict[str, float] = {}
        reasons: dict[str, str] = {}
        rejected: list[str] = []

        if sample.active_build_descendants:
            build_score = 0.82 + min(sample.active_build_descendants, 2) * 0.06
            if sample.hot_descendants:
                build_score += 0.05
            scores["building"] = min(build_score, 0.97)
            reasons["building"] = sample.reason or "build activity detected"
        elif sample.build_descendants:
            rejected.append("building quiet only")

        if sample.meaningful_descendants:
            tooling_score = 0.66 + min(sample.meaningful_descendants, 2) * 0.07
            if sample.hot_descendants:
                tooling_score += 0.07
            if sample.specific_shell_descendants:
                tooling_score += 0.03
            scores["tooling"] = min(tooling_score, 0.95)
            reasons["tooling"] = sample.reason or "child tool path active"
        elif sample.descendants:
            if sample.shell_descendants == sample.descendants:
                rejected.append("tooling held: shell-only")
            else:
                rejected.append("tooling held: descendants quiet")

        if sample.descendants and not sample.meaningful_descendants:
            if self.last_tool_activity_at > 0.0 and quiet_for >= WAITING_GRACE_SECONDS:
                waiting_score = 0.70
                if sample.shell_descendants != sample.descendants:
                    waiting_score += 0.04
                scores["waiting"] = min(waiting_score, 0.90)
                reasons["waiting"] = f"work quiet for {quiet_for:.1f}s"
            elif self.last_tool_activity_at <= 0.0:
                rejected.append("waiting held: no prior work")
            else:
                rejected.append(f"waiting held: quiet {quiet_for:.1f}s")

        if not sample.descendants and sample.reasoning_hit:
            thinking_score = 0.84
            if root_hot:
                thinking_score += 0.05
            elif self.root_activity_streak:
                thinking_score += 0.03
            thinking_score += min(sample.root_cpu_delta, 0.12) * 0.25
            scores["thinking"] = min(thinking_score, 0.98)
            reasons["thinking"] = f"rollout reasoning hit {sample.reasoning_age:.1f}s ago"
        elif not sample.descendants and root_hot:
            thinking_score = 0.44 + min(self.root_activity_streak, ROOT_THINKING_MIN_STREAK + 2) * 0.12
            thinking_score += min(sample.root_cpu_delta, 0.18) * 0.70
            scores["thinking"] = min(thinking_score, 0.96)
            reasons["thinking"] = f"app-server cpu +{sample.root_cpu_delta:.3f} for {self.root_activity_streak} polls"
        elif sample.descendants:
            rejected.append("thinking held: child path present")
        elif sample.root_cpu_delta > 0.0:
            rejected.append("thinking held: root pulse light")
        elif sample.reasoning_detail:
            rejected.append(f"thinking held: {sample.reasoning_detail}")

        idle_reason = sample.reason or "quiet"
        if sample.descendants and not sample.meaningful_descendants:
            idle_reason = "signals weak; staying quiet"
        elif sample.root_cpu_delta > 0.0 and not sample.descendants:
            idle_reason = "root pulse below confidence gate"
        elif not sample.root_pid:
            idle_reason = "no app-server"
        elif sample.reasoning_detail:
            idle_reason = sample.reasoning_detail

        candidate_state = "idle"
        candidate_score = 0.0
        chosen_state = "idle"
        hint = ""
        reason = idle_reason
        if scores:
            candidate_state, candidate_score = max(scores.items(), key=lambda item: item[1])
            gate = STATE_CONFIDENCE_GATES[candidate_state]
            if candidate_score >= gate:
                chosen_state = candidate_state
                reason = reasons[candidate_state]
                if chosen_state in {"building", "tooling"}:
                    hint = sample.hint
            else:
                rejected.insert(0, f"{candidate_state} below gate {candidate_score:.2f}/{gate:.2f}")

        if chosen_state in ACTIVE_VISUAL_STATES:
            self.delivered_until = 0.0
            return SensorDecision(chosen_state, candidate_state, candidate_score, hint, reason, tuple(rejected[:3]))

        if chosen_state == "idle" and had_active_visual:
            self.delivered_until = now + DELIVERED_HOLD_SECONDS
            return SensorDecision("delivered", candidate_state, candidate_score, "", "recent work finished", tuple(rejected[:3]))

        if chosen_state == "idle" and self.delivered_until > now:
            return SensorDecision("delivered", candidate_state, candidate_score, "", "recent work finished", tuple(rejected[:3]))

        return SensorDecision("idle", candidate_state, candidate_score, "", reason, tuple(rejected[:3]))

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
            decision = self._derive_state(sample, now)
            self._record_sensor_trace(sample, decision)
            self._set_visual_state(decision.chosen_state, decision.hint, decision.reason)

        self.root.after(self._next_poll_delay_ms(None if error_text else sample, error_text), self._schedule_poll)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = CompanionApp()
    app.run()


if __name__ == "__main__":
    main()
