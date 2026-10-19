# PyInstaller build of the widget, run from the repo root:
#   pyinstaller --noconfirm packaging/claude_usage.spec
# Windows: dist/Claude Usage/Claude Usage.exe (packed by packaging/windows.iss)
# macOS:   dist/Claude Usage.app
# APP_VERSION (env) sets the version shown in the app bundle.
import os
import sys

NAME = "Claude Usage"
VERSION = os.environ.get("APP_VERSION", "0.0.0")
MAC = sys.platform == "darwin"
ROOT = os.path.dirname(SPECPATH)  # SPECPATH: this file's folder, set by PyInstaller
ASSETS = os.path.join(ROOT, "assets")
ICON = os.path.join(ASSETS, "icon.icns" if MAC else "icon.ico")

a = Analysis(
    [os.path.join(ROOT, "src", "claude_usage_widget.pyw")],
    datas=[(os.path.join(ASSETS, "icon.png"), "assets"),
           (os.path.join(ASSETS, "icon_mac.png"), "assets")],
    excludes=["unittest", "pydoc", "doctest", "email.test", "test"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=NAME,
    console=False,
    icon=ICON,
)
coll = COLLECT(exe, a.binaries, a.datas, name=NAME)

if MAC:
    app = BUNDLE(
        coll,
        name=f"{NAME}.app",
        icon=ICON,
        bundle_identifier="io.github.pholsen.claude-usage-widget",
        version=VERSION,
        info_plist={
            "CFBundleDisplayName": NAME,
            "CFBundleShortVersionString": VERSION,
            "LSMinimumSystemVersion": "11.0",
            "NSHighResolutionCapable": True,
        },
    )
