# Script para crear acceso directo en el escritorio
# Ejecutar este script una vez para crear el acceso directo

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Dashboard Gastos.lnk")
$Shortcut.TargetPath = "$PSScriptRoot\ejecutar_dashboard.bat"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.IconLocation = "$PSScriptRoot\ejecutar_dashboard.bat,0"
$Shortcut.Description = "Dashboard de Gastos del Hogar - Ejecutar localmente"
$Shortcut.Save()

Write-Host "✅ Acceso directo creado en el escritorio: 'Dashboard Gastos.lnk'" -ForegroundColor Green
Write-Host "🖱️  Ahora puedes hacer doble clic en el escritorio para ejecutar el dashboard" -ForegroundColor Cyan

Read-Host "Presiona Enter para continuar"
