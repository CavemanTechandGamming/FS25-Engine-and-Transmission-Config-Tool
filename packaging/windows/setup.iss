; =============================================================================
; FS25 Engine and Transmission Config Tool — Windows installer (Inno Setup 6)
;
; Defines (passed by scripts/build_app.bat / CI):
;   MyAppVersion          e.g. 1.0.0
;   SourceExe             full path to the portable onefile .exe
;   OutputDir             folder for the Setup .exe
;   OutputBaseFilename    e.g. FS25 Engine and Transmission Config Tool-1.0.0-Setup
; =============================================================================

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#ifndef SourceExe
  #define SourceExe "FS25 Engine and Transmission Config Tool.exe"
#endif
#ifndef OutputDir
  #define OutputDir "."
#endif
#ifndef OutputBaseFilename
  #define OutputBaseFilename "FS25 Engine and Transmission Config Tool-Setup"
#endif

#define MyAppName "FS25 Engine and Transmission Config Tool"
#define MyAppPublisher "CavemanTechandGamming"
#define MyAppURL "https://github.com/CavemanTechandGamming/FS25-Engine-and-Transmission-Config-Tool"
#define MyAppExeName "FS25 Engine and Transmission Config Tool.exe"

[Setup]
; Fixed AppId so upgrades / uninstall stay consistent across versions
AppId={{8F3C9E2A-4B71-4D6E-9A1C-2E5F7B8D0C41}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\..\LICENSE
OutputDir={#OutputDir}
OutputBaseFilename={#OutputBaseFilename}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\..\assets\app_icon.ico
VersionInfoVersion={#MyAppVersion}.0
VersionInfoProductName={#MyAppName}
VersionInfoCompany={#MyAppPublisher}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceExe}"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
