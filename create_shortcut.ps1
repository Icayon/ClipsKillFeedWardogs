$WshShell = New-Object -ComObject WScript.Shell

# Acceso directo en el Escritorio
$ShortcutPath = "$([System.Environment]::GetFolderPath('Desktop'))\AutoClip Studio.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "E:\Videos OBS\AutoClip_AI\dist\AutoClip_Studio\AutoClip_Studio.exe"
$Shortcut.WorkingDirectory = "E:\Videos OBS\AutoClip_AI\dist\AutoClip_Studio"
$Shortcut.IconLocation = "E:\Videos OBS\AutoClip_AI\app_icon.ico, 0"
$Shortcut.Description = "AutoClip Studio Pro - Detector de Killfeed & Editor de Highlights"
$Shortcut.Save()

# Acceso directo en E:\Videos OBS
$ShortcutFolder = "E:\Videos OBS\AutoClip Studio.lnk"
$Shortcut2 = $WshShell.CreateShortcut($ShortcutFolder)
$Shortcut2.TargetPath = "E:\Videos OBS\AutoClip_AI\dist\AutoClip_Studio\AutoClip_Studio.exe"
$Shortcut2.WorkingDirectory = "E:\Videos OBS\AutoClip_AI\dist\AutoClip_Studio"
$Shortcut2.IconLocation = "E:\Videos OBS\AutoClip_AI\app_icon.ico, 0"
$Shortcut2.Description = "AutoClip Studio Pro - Detector de Killfeed & Editor de Highlights"
$Shortcut2.Save()

Write-Output "Shortcuts created successfully on Desktop and OBS folder!"
