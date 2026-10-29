# 1000 transacciones en la base PostgreSQL de demostracion `quechua_wanka_demo`, registradas a traves de
# los procedimientos almacenados (BASE_DATOS=postgres). La base se recrea vacia (pide confirmacion salvo
# con -Forzar); ninguna otra base se toca. Credenciales: backend\.env (no se imprimen).
param(
    [switch]$Forzar,
    [int]$Transacciones = 1000,
    [string]$Salida = (Join-Path (Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path "docs\evidencias\cierre_u3\data_masiva") "postgres")
)
. "$PSScriptRoot\_comun.ps1"
Exigir-Python
Comprobar-Env

if ((Estado-Api) -eq 200) {
    Escribir-Aviso "Hay una API en marcha; si usa quechua_wanka_demo, detengala antes (01_arrancar_app.ps1 -Detener)."
}
if (-not $Forzar) {
    $r = Read-Host "Se recreara la base quechua_wanka_demo (las demas no se tocan). Continuar? (s/N)"
    if ($r -notmatch '^(s|S|si|SI|y|Y)$') { Escribir-Aviso "Cancelado."; exit 1 }
}

$env:BASE_DATOS  = "postgres"
$env:POSTGRES_DB = "quechua_wanka_demo"
Push-Location -LiteralPath $Backend
try {
    Escribir-Paso "Recreando quechua_wanka_demo ..."
    & $Python "scripts\preparar_base_demo_postgres.py"
    if ($LASTEXITCODE -ne 0) {
        Escribir-Error "No se pudo preparar la base. Compruebe que PostgreSQL esta en marcha y las variables POSTGRES_* de backend\.env."
        exit $LASTEXITCODE
    }
    Escribir-Paso "Generando $Transacciones transacciones (origen carga) por los procedimientos almacenados ..."
    $codigo = Ejecutar-Y-Guardar (Join-Path $Salida "consola.txt") {
        & $Python "scripts\generar_transacciones.py" "$Transacciones" "$Salida"
    }
} finally {
    Pop-Location
}
if ($codigo -ne 0) { Escribir-Error "La carga fallo (codigo $codigo)."; exit $codigo }
Escribir-Ok "Listo. Evidencia en $Salida"
Escribir-Ok "Para verla en la app:  scripts\demo\01_arrancar_app.ps1 -Base postgres -BaseDemo"
