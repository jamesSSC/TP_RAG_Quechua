# 800 transacciones con origen `carga` sobre backend\carga.db (una base aparte que nunca es la real).
# Si la base ya existe, la recrea (pide confirmacion salvo con -Forzar). Los resultados van a
# docs\evidencias\cierre_u3\data_masiva\sqlite\ (CSV, JSON de resumen y salida de consola).
param(
    [switch]$Forzar,
    [int]$Transacciones = 800,
    [string]$Salida = (Join-Path (Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path "docs\evidencias\cierre_u3\data_masiva") "sqlite")
)
. "$PSScriptRoot\_comun.ps1"
Exigir-Python

if ((Estado-Api) -eq 200) {
    Escribir-Aviso "Hay una API en marcha; si usa carga.db, detengala antes (01_arrancar_app.ps1 -Detener)."
}
if (Test-Path -LiteralPath $CargaDb) {
    if (-not $Forzar) {
        $r = Read-Host "backend\carga.db ya existe y se va a recrear (la base real NO se toca). Continuar? (s/N)"
        if ($r -notmatch '^(s|S|si|SI|y|Y)$') { Escribir-Aviso "Cancelado."; exit 1 }
    }
    Remove-Item -LiteralPath $CargaDb -Force
    Escribir-Paso "Base anterior eliminada."
}

# Defensa: jamas escribir sobre la base real.
$real = Join-Path $Backend "quechua_wanka.db"
if ($CargaDb -eq $real) { Escribir-Error "carga.db no puede ser la base real."; exit 6 }

$env:BASE_DATOS  = "sqlite"
$env:RUTA_SQLITE = $CargaDb
Escribir-Paso "Generando $Transacciones transacciones (origen carga) en backend\carga.db ..."
Push-Location -LiteralPath $Backend
try {
    $codigo = Ejecutar-Y-Guardar (Join-Path $Salida "consola.txt") {
        & $Python "scripts\generar_transacciones.py" "$Transacciones" "$Salida"
    }
} finally {
    Pop-Location
}
if ($codigo -ne 0) { Escribir-Error "La carga fallo (codigo $codigo)."; exit $codigo }
Escribir-Ok "Listo. Evidencia en $Salida"
Escribir-Ok "Para verla en la app:  scripts\demo\01_arrancar_app.ps1 -BaseDemo"
