# PyInstaller build of the widget: pyinstaller --noconfirm claude_usage.spec
# Windows: dist/Claude Usage/Claude Usage.exe (packed by installer/windows.iss)
# macOS:   dist/Claude Usage.app
# APP_VERSION (env) sets the version shown in the app bundle.
import os
import sys

NAME = "Claude Usage"
VERSION = os.environ.get("APP_VERSION", "0.0.0")
MAC = sys.platform == "darwin"

a = Analysis(
    ["claude_usage_widget.pyw"],
    datas=[("assets/icon.png", "assets"), ("assets/icon_mac.png", "assets")],
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
    icon="Claude Usage.app/Contents/Resources/icon.icns" if MAC else "assets/icon.ico",
)
coll = COLLECT(exe, a.binaries, a.datas, name=NAME)

if MAC:
    app = BUNDLE(
        coll,
        name=f"{NAME}.app",
        icon="Claude Usage.app/Contents/Resources/icon.icns",
        bundle_identifier="io.github.pholsen.claude-usage-widget",
        version=VERSION,
        info_plist={
            "CFBundleDisplayName": NAME,
            "CFBundleShortVersionString": VERSION,
            "LSMinimumSystemVersion": "11.0",
            "NSHighResolutionCapable": True,
        },
    )
