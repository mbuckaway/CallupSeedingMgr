; -- CallupSeedingMgr.iss --

[Setup]
#include "inno_setup.txt"
ArchitecturesInstallIn64BitMode=x64
DefaultDirName={pf}\CallupSeedingMgr
DefaultGroupName=CallupSeedingMgr
UninstallDisplayIcon={app}\CallupSeedingMgr.exe
Compression=lzma
SolidCompression=yes
SourceDir=dist\CallupSeedingMgr
OutputDir=..\..\install
OutputBaseFilename=CallupSeedingMgr_Setup
ChangesAssociations=yes

[Registry]
; Automatically configure CallupSeedingMgr to launch .smr files.
Root: HKCR; Subkey: ".smr"; ValueType: string; ValueName: ""; ValueData: "CallupSeedingMgr"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "CallupSeedingMgr"; ValueType: string; ValueName: ""; ValueData: "CallupSeedingMgr Race File"; Flags: uninsdeletekey
Root: HKCR; Subkey: "CallupSeedingMgr\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\CallupSeedingMgr.exe,0"
Root: HKCR; Subkey: "CallupSeedingMgr\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\CallupSeedingMgr.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\CallupSeedingMgr"; Filename: "{app}\CallupSeedingMgr.exe"
Name: "{userdesktop}\CallupSeedingMgr"; Filename: "{app}\CallupSeedingMgr.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CallupSeedingMgr.exe"; Description: "Launch CallupSeedingMgr"; Flags: nowait postinstall skipifsilent
