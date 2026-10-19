; Inno Setup script: packs the PyInstaller build (dist\Claude Usage) into ClaudeUsage-Setup-<version>.exe
; Build: iscc /DMyAppVersion=1.0.0 packaging\windows.iss
; Installs per user (no admin prompt) into %LOCALAPPDATA%\Programs\Claude Usage.

#define MyAppName "Claude Usage"
#define MyAppExe "Claude Usage.exe"
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

[Setup]
AppId={{51E4A9F9-CAC7-4A7B-A5D0-D60E274FA1F9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher=pholsen
AppPublisherURL=https://github.com/pholsen/claude-usage-widget
AppSupportURL=https://github.com/pholsen/claude-usage-widget/issues
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=ClaudeUsage-Setup-{#MyAppVersion}
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExe}
UninstallDisplayName={#MyAppName}
WizardStyle=modern
Compression=lzma2
SolidCompression=yes
CloseApplications=force
ShowLanguageDialog=auto

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "tr"; MessagesFile: "compiler:Languages\Turkish.isl"

[CustomMessages]
en.AutoStart=Start with Windows
tr.AutoStart=Windows açılışında başlat

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startup"; Description: "{cm:AutoStart}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\Claude Usage\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start menu folder "Claude Usage" with the app and its uninstaller
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"; Tasks: startup

[Run]
Filename: "{app}\{#MyAppExe}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/f /im ""{#MyAppExe}"""; Flags: runhidden; RunOnceId: "StopWidget"
