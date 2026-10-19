#!/bin/bash
# macOS launcher: double-click to start the widget in the background; this Terminal window can be closed.
cd "$(dirname "$0")"
nohup python3 claude_usage_widget.pyw >/dev/null 2>&1 &
disown
exit 0
