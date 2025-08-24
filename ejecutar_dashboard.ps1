# Dashboard de Gastos del Hogar - Launcher
# Ejecuta el dashboard de forma fácil y segura

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DASHBOARD DE GASTOS DEL HOGAR" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio del script
Set-Location $PSScriptRoot

# Verificar entorno virtual
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Green
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "❌ Error: No se encontró el entorno virtual" -ForegroundColor Red
    Write-Host "💡 Ejecuta: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "Presiona Enter para continuar"
    exit
}

# Verificar dependencias
try {
    python -c "import streamlit" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "🔧 Instalando dependencias..." -ForegroundColor Yellow
        pip install -r requirements.txt
    }
} catch {
    Write-Host "❌ Error verificando dependencias" -ForegroundColor Red
}

# Verificar puerto disponible
$portCheck = netstat -an | Select-String ":8501"
if ($portCheck) {
    Write-Host "⚠️  Puerto 8501 ocupado. Cerrando procesos anteriores..." -ForegroundColor Yellow
    taskkill /F /IM streamlit.exe 2>$null
    Start-Sleep -Seconds 2
}

# Ejecutar dashboard
Write-Host "🚀 Iniciando dashboard en http://localhost:8501" -ForegroundColor Green
Write-Host "💡 Para detener el dashboard, presiona Ctrl+C" -ForegroundColor Cyan
Write-Host ""

# Abrir navegador automáticamente
Start-Sleep -Seconds 3
Start-Process "http://localhost:8501"

# Ejecutar streamlit
streamlit run dashboard_simple.py

Write-Host "👋 Dashboard finalizado. ¡Hasta la próxima!" -ForegroundColor Green
Read-Host "Presiona Enter para cerrar"
