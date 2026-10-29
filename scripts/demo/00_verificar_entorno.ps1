# Verifica que la PC esta lista para la demostracion (lo hace backend/scripts/verificar_entorno_demo.py).
# Uso:  powershell -ExecutionPolicy Bypass -File scripts\demo\00_verificar_entorno.ps1
. "$PSScriptRoot\_comun.ps1"
Exigir-Python

$verificador = Join-Path $Backend "scripts\verificar_entorno_demo.py"
if (-not (Test-Path -LiteralPath $verificador)) {
    Escribir-Aviso "Todavia no existe backend\scripts\verificar_entorno_demo.py (llega con el bloque P0-B7)."
    Escribir-Aviso "No se puede verificar el entorno; el script termina con codigo 2."
    exit 2
}

Escribir-Paso "Verificando el entorno de la demostracion..."
Push-Location -LiteralPath $Backend
try {
    & $Python $verificador
    $codigo = $LASTEXITCODE
} finally {
    Pop-Location
}
if ($codigo -eq 0) { Escribir-Ok "Entorno listo." } else { Escribir-Error "El entorno no esta listo (codigo $codigo)." }
exit $codigo
