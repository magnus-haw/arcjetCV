"""
Native file dialogs for the web interface.

The browser cannot hand a page the real path of a file on disk, but the local
arcjetCV engine can: it opens the operating system's own Open or Save window
(Finder on macOS, Explorer on Windows, GTK/Tk on Linux) and returns the paths
the user picked. Each dialog runs in a short-lived subprocess so it never
touches the Flask threads.
"""

import json
import os
import shutil
import subprocess
import sys
import threading

_LOCK = threading.Lock()

# AppleScript run as `osascript - <args>`; arguments are passed as argv so
# titles and paths are never interpolated into the script text.
_MAC_OPEN = r"""
on run argv
    set thePrompt to item 1 of argv
    set theDir to item 2 of argv
    set multi to (item 3 of argv) is "1"
    set theTypes to {}
    if (count of argv) > 3 then set theTypes to items 4 thru -1 of argv
    activate
    if theTypes is {} then
        set picked to choose file with prompt thePrompt default location (POSIX file theDir) multiple selections allowed multi
    else
        set picked to choose file with prompt thePrompt of type theTypes default location (POSIX file theDir) multiple selections allowed multi
    end if
    if class of picked is not list then set picked to {picked}
    set out to ""
    repeat with f in picked
        set out to out & POSIX path of f & linefeed
    end repeat
    return out
end run
"""

_MAC_SAVE = r"""
on run argv
    activate
    set picked to choose file name with prompt (item 1 of argv) default name (item 3 of argv) default location (POSIX file (item 2 of argv))
    return POSIX path of picked
end run
"""

_TK = r"""
import json, sys, tkinter as tk
from tkinter import filedialog
a = json.loads(sys.argv[1])
root = tk.Tk(); root.withdraw()
try:
    root.attributes("-topmost", True)
except Exception:
    pass
types = [("Supported files", " ".join("*" + e for e in a["exts"]))] if a["exts"] else []
types.append(("All files", "*.*"))
if a["mode"] == "save":
    p = filedialog.asksaveasfilename(parent=root, title=a["title"], initialdir=a["start"],
                                     initialfile=a["name"], defaultextension=".json", filetypes=types)
    out = [p] if p else []
elif a["multi"]:
    out = list(filedialog.askopenfilenames(parent=root, title=a["title"], initialdir=a["start"], filetypes=types))
else:
    p = filedialog.askopenfilename(parent=root, title=a["title"], initialdir=a["start"], filetypes=types)
    out = [p] if p else []
root.destroy()
print(json.dumps(out))
"""


class DialogUnavailable(RuntimeError):
    pass


class DialogBusy(RuntimeError):
    pass


def available():
    if sys.platform == "darwin":
        return shutil.which("osascript") is not None
    if sys.platform.startswith("linux") and not (
        os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    ):
        return False
    try:
        import tkinter  # noqa: F401
    except Exception:
        return False
    return True


def _start_dir(start):
    start = os.path.expanduser(start or "")
    if start and os.path.isfile(start):
        start = os.path.dirname(start)
    return start if start and os.path.isdir(start) else os.path.expanduser("~")


def _run(cmd, stdin=None):
    proc = subprocess.run(cmd, input=stdin, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def _mac(mode, title, start, multi, exts, name):
    if mode == "save":
        code, out, err = _run(["osascript", "-", title, start, name], _MAC_SAVE)
    else:
        types = [e.lstrip(".") for e in exts]
        code, out, err = _run(
            ["osascript", "-", title, start, "1" if multi else "0", *types], _MAC_OPEN
        )
    if code != 0:
        if "-128" in err:  # User canceled.
            return []
        raise RuntimeError(err.strip() or "The file window could not be opened.")
    return [line for line in out.splitlines() if line.strip()]


def _tk(mode, title, start, multi, exts, name):
    args = json.dumps({"mode": mode, "title": title, "start": start, "multi": multi,
                       "exts": sorted(exts), "name": name})
    code, out, err = _run([sys.executable, "-c", _TK, args])
    if code != 0:
        raise DialogUnavailable(err.strip().splitlines()[-1] if err.strip() else "Tk failed")
    return json.loads(out.strip().splitlines()[-1] or "[]")


def ask(mode="open", title="Open", start=None, multi=False, exts=(), name="untitled.json"):
    """
    Show a native Open or Save window and return the chosen paths
    (an empty list when the user cancels).
    """
    if not available():
        raise DialogUnavailable("No desktop session for a native file window.")
    if not _LOCK.acquire(blocking=False):
        raise DialogBusy("A file window is already open.")
    try:
        start = _start_dir(start)
        fn = _mac if sys.platform == "darwin" else _tk
        paths = fn(mode, title, start, bool(multi), list(exts), name)
        return [os.path.abspath(p) for p in paths]
    finally:
        _LOCK.release()
