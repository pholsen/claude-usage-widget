"""Claude usage widget (desktop, always on top, no console).

Shows the REAL session (5 hour) and weekly percentages from
claude.ai > Settings > Usage. Data comes from the endpoint Claude Code's
/usage command uses, authenticated with Claude Code's stored login
(Windows/Linux: ~/.claude/.credentials.json, macOS: Keychain).
No estimates, no calibration.

Install: the Windows installer / macOS disk image from the GitHub releases page.
From source: double-click this file on Windows (.pyw opens no console),
or run: python3 src/claude_usage_widget.pyw
Starts at the bottom-left of the main screen on every launch.
Drag: left click + drag | Close: right click (Mac: ctrl + click) | Refresh now: double click
Red dot at top-right: the last refresh failed, the value shown is stale.

Interface language follows the system (Turkish or English);
override with CLAUDE_WIDGET_LANG=tr or CLAUDE_WIDGET_LANG=en.
"""
import ctypes
import json
import locale
import os
import subprocess
import sys

IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"

# hide the console window even when started with python.exe (Windows)
if IS_WIN:
    try:
        _hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if _hwnd:
            ctypes.windll.user32.ShowWindow(_hwnd, 0)
    except Exception:
        pass

import tkinter as tk
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# in a PyInstaller build the assets are unpacked to sys._MEIPASS, in the repo they sit next to src/
BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
ICON = BASE / "assets" / ("icon_mac.png" if IS_MAC else "icon.png")
REFRESH_SECONDS = 60
USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
KEYCHAIN_SERVICE = "Claude Code-credentials"  # where Claude Code keeps its login on macOS

BG = "#1f1e1d"
FG = "#f5f4ef"
MUTED = "#a09d96"
ACCENT = "#d97757"
TRACK = "#3a3835"
WARN = "#e5484d"


# ---------- language ----------
STRINGS = {
    "en": {
        "session": "Session", "week": "Week", "no_session": "no active session",
        "loading": "Loading…", "no_login": "Not logged in to Claude Code",
        "unauthorized": "Open Claude Code once", "server": "Server error {}",
        "offline": "No internet", "pct": "{}%",
        "days": "{d}d {h}h", "hours": "{h}h {m}m",
    },
    "tr": {
        "session": "Oturum", "week": "Hafta", "no_session": "aktif oturum yok",
        "loading": "Yükleniyor…", "no_login": "Claude Code girişi yok",
        "unauthorized": "Claude Code'u bir kez aç", "server": "Sunucu hatası {}",
        "offline": "İnternet yok", "pct": "%{}",
        "days": "{d}g {h}sa", "hours": "{h}sa {m}dk",
    },
}


def system_language():
    forced = os.environ.get("CLAUDE_WIDGET_LANG", "").lower()[:2]
    if forced in STRINGS:
        return forced
    if IS_WIN:
        try:
            if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x1F:  # LANG_TURKISH
                return "tr"
        except Exception:
            pass
        return "en"
    if IS_MAC:
        try:
            out = subprocess.run(["defaults", "read", "-g", "AppleLanguages"],
                                 capture_output=True, text=True, timeout=5).stdout
            first = out.strip("()\n ").split(",")[0].strip(' "\n')
            return "tr" if first.lower().startswith("tr") else "en"
        except (OSError, subprocess.SubprocessError):
            pass
    lang = os.environ.get("LANG") or (locale.getlocale()[0] or "")
    return "tr" if lang.lower().startswith("tr") else "en"


T = STRINGS[system_language()]


# ---------- reading data ----------
def credential_paths():
    paths = []
    env = os.environ.get("CLAUDE_CONFIG_DIR")
    if env:
        for p in env.split(","):
            paths.append(Path(p.strip()) / ".credentials.json")
    paths.append(Path.home() / ".claude" / ".credentials.json")
    return paths


def token_from(text):
    try:
        oauth = json.loads(text).get("claudeAiOauth") or {}
    except (ValueError, AttributeError):
        return None
    return oauth.get("accessToken")


def keychain_token():
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return token_from(out.stdout) if out.returncode == 0 else None


def access_token():
    # re-read every time: Claude Code updates the stored login when it refreshes the token
    if IS_MAC:
        token = keychain_token()
        if token:
            return token
    for p in credential_paths():
        try:
            token = token_from(p.read_text(encoding="utf-8"))
        except OSError:
            continue
        if token:
            return token
    return None


def fetch_usage():
    token = access_token()
    if not token:
        raise RuntimeError(T["no_login"])
    req = urllib.request.Request(USAGE_URL, headers={
        "Authorization": f"Bearer {token}",
        "anthropic-beta": "oauth-2025-04-20",
        "User-Agent": "claude-usage-widget",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise RuntimeError(T["unauthorized"])
        raise RuntimeError(T["server"].format(e.code))
    except urllib.error.URLError:
        raise RuntimeError(T["offline"])


def parse_block(block):
    """Returns (percent, reset time) from an API block."""
    if not block or block.get("utilization") is None:
        return 0.0, None
    end = None
    if block.get("resets_at"):
        try:
            end = datetime.fromisoformat(block["resets_at"].replace("Z", "+00:00"))
        except ValueError:
            pass
    return float(block["utilization"]), end


# ---------- interface ----------
W, H = 214, 100
PAD = 14
MARGIN = 12
DOCK = 80  # macOS: room to stay above the Dock (Tk cannot read the work area there)


def font(size, bold=False):
    if IS_WIN:
        return ("Segoe UI Semibold" if bold else "Segoe UI", size)
    weight = "bold" if bold else "normal"
    if IS_MAC:
        # Tk on macOS treats points as 72 dpi; scale up to match the Windows size
        return ("Helvetica Neue", round(size * 4 / 3), weight)
    return ("DejaVu Sans", size, weight)


def bottom_left(root):
    """Bottom-left corner of the main screen, just above the taskbar / Dock."""
    left, bottom = 0, root.winfo_screenheight()
    if IS_WIN:
        try:
            rect = (ctypes.c_long * 4)()
            if ctypes.windll.user32.SystemParametersInfoW(48, 0, rect, 0):  # SPI_GETWORKAREA
                left, bottom = rect[0], rect[3]
        except Exception:
            pass
    elif IS_MAC:
        bottom -= DOCK
    return left + MARGIN, bottom - H - MARGIN


def rrect(c, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


def left_text(end, now):
    if end is None:
        return T["no_session"]
    secs = max(int((end - now).total_seconds()), 0)
    d, rem = divmod(secs, 86400)
    h, m = divmod(rem // 60, 60)
    return T["days"].format(d=d, h=h) if d else T["hours"].format(h=h, m=m)


def make_transparent(r):
    """Makes the window background transparent; returns the clear colour (BG if unsupported)."""
    try:
        if IS_MAC:
            r.attributes("-transparent", True)
            clear = "systemTransparent"
        else:
            clear = "#010101"
            r.attributes("-transparentcolor", clear)
        r.configure(bg=clear)
        return clear
    except tk.TclError:
        r.configure(bg=BG)
        return BG


class Widget:
    def __init__(self):
        self.root = tk.Tk()
        r = self.root
        r.title("Claude usage")
        try:  # Dock icon on macOS, window icon elsewhere
            self.icon = tk.PhotoImage(file=str(ICON))
            r.iconphoto(True, self.icon)
        except tk.TclError:
            pass
        r.overrideredirect(True)
        r.attributes("-topmost", True)
        clear = make_transparent(r)

        x, y = bottom_left(r)
        r.geometry(f"{W}x{H}+{x}+{y}")

        self.canvas = tk.Canvas(r, width=W, height=H, bg=clear,
                                highlightthickness=0)
        self.canvas.pack()
        c = self.canvas
        c.bind("<ButtonPress-1>", self.start_move)
        c.bind("<B1-Motion>", self.do_move)
        c.bind("<Double-Button-1>", lambda e: self.refresh())
        # right click: Button-3 on Windows/Linux, Button-2 or ctrl + click on macOS
        close_buttons = ("<Button-2>", "<Control-Button-1>") if IS_MAC else ("<Button-3>",)
        for seq in close_buttons:
            c.bind(seq, lambda e: r.destroy())

        self.data = None   # last successful response
        self.error = None  # error of the last refresh
        self.after_id = None
        self.refresh()

    # --- dragging ---
    def start_move(self, e):
        self.dx, self.dy = e.x_root - self.root.winfo_x(), e.y_root - self.root.winfo_y()

    def do_move(self, e):
        self.root.geometry(f"+{e.x_root - self.dx}+{e.y_root - self.dy}")

    # --- drawing ---
    def draw_row(self, y, title, pct, end, now):
        c = self.canvas
        c.create_text(PAD, y, text=title, anchor="nw", fill=FG,
                      font=font(9, bold=True))
        c.create_text(PAD + 56, y + 2, text=left_text(end, now), anchor="nw",
                      fill=MUTED, font=font(8))
        frac = pct / 100
        color = ACCENT if frac < 0.9 else WARN
        c.create_text(W - PAD, y - 2, text=T["pct"].format(round(pct)), anchor="ne",
                      fill=color, font=font(13, bold=True))
        by = y + 24
        rrect(c, PAD, by, W - PAD, by + 5, 2, fill=TRACK, outline="")
        if frac > 0:
            fw = max(5, (W - 2 * PAD) * min(frac, 1.0))
            rrect(c, PAD, by, PAD + fw, by + 5, 2, fill=color, outline="")

    def redraw(self):
        c = self.canvas
        c.delete("all")
        rrect(c, 1, 1, W - 1, H - 1, 14, fill=BG, outline="#2e2c2a")
        d = self.data
        if d is None:
            c.create_text(W / 2, H / 2, text=self.error or T["loading"],
                          fill=WARN if self.error else MUTED, width=W - 2 * PAD,
                          justify="center", font=font(9))
            return
        now = datetime.now(timezone.utc)
        self.draw_row(16, T["session"], *parse_block(d.get("five_hour")), now)
        self.draw_row(58, T["week"], *parse_block(d.get("seven_day")), now)
        if self.error:  # showing stale data
            c.create_oval(W - 10, 5, W - 5, 10, fill=WARN, outline="")

    def refresh(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        try:
            self.data = fetch_usage()
            self.error = None
        except Exception as ex:  # keep the widget alive and the last known value on screen
            self.error = str(ex)
        self.redraw()
        self.after_id = self.root.after(REFRESH_SECONDS * 1000, self.refresh)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Widget().run()
