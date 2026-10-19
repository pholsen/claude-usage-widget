@echo off
rem Creates "Claude Usage" shortcuts with the widget icon (Desktop + Start menu, optionally Startup).
setlocal
set "DIR=%~dp0"
set "PYW="
for /f "delims=" %%P in ('where pythonw 2^>nul') do if not defined PYW set "PYW=%%P"
if not defined PYW if exist "%SystemRoot%\pyw.exe" set "PYW=%SystemRoot%\pyw.exe"
if not defined PYW (
  echo pythonw.exe not found. Install Python from https://www.python.org/downloads/
  pause
  exit /b 1
)
set "STARTUP=0"
choice /c YN /m "Start the widget automatically with Windows"
if not errorlevel 2 set "STARTUP=1"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$sh = New-Object -ComObject WScript.Shell;" ^
  "$dirs = @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'));" ^
  "if ($env:STARTUP -eq '1') { $dirs += [Environment]::GetFolderPath('Startup') };" ^
  "foreach ($d in $dirs) {" ^
  "  $l = $sh.CreateShortcut((Join-Path $d 'Claude Usage.lnk'));" ^
  "  $l.TargetPath = $env:PYW;" ^
  "  $l.Arguments = [char]34 + $env:DIR + 'claude_usage_widget.pyw' + [char]34;" ^
  "  $l.WorkingDirectory = $env:DIR;" ^
  "  $l.IconLocation = $env:DIR + 'assets\icon.ico';" ^
  "  $l.Description = 'Claude usage widget';" ^
  "  $l.Save(); Write-Host ('Created ' + $l.FullName) }"
echo.
echo Done. Open the widget with the "Claude Usage" shortcut.
pause
