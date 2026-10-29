# Arranca el backend (uvicorn en 127.0.0.1:8000) y el frontend (Vite en 127.0.0.1:5173) y abre el navegador.
#
#   -Base sqlite|postgres   motor de la base (por defecto sqlite)
#   -BaseDemo               usa la base de demostracion: backend\carga.db (sqlite) o quechua_wanka_demo (postgres)
#   -SinNavegador           no abre el navegador
#   -Detener                detiene los servidores que arranco este script
#
# Es idempotente: si la API ya responde, no arranca otra.
param(
    [ValidateSet("sqlite", "postgres")] [string]$Base = "sqlite",
    [switch]$BaseDemo,
    [switch]$SinNavegador,
    [switch]$Detener
)
. "$PSScriptRoot\_comun.ps1"

if ($Detener) { Detener-Servidores; exit 0 }
Exigir-Python
Comprobar-Env

if ((Estado-Api) -eq 200) {
    Escribir-Aviso "La API ya responde en http://127.0.0.1:${PuertoApi}: no se arranca otra. Use -Detener para pararla."
    exit 0
}
foreach ($p in @($PuertoApi, $PuertoWeb)) {
    if (Puerto-Ocupado $p) {
        Escribir-Error "El puerto $p esta ocupado por otro programa. Cierrelo e intente de nuevo."
        exit 3
    }
}

# --- Base de datos del backend (variables de entorno solo para los procesos hijos) ---
$env:BASE_DATOS = $Base
if ($BaseDemo) {
    if ($Base -eq "sqlite") {
        if (-not (Test-Path -LiteralPath $CargaDb)) {
            Escribir-Error "No existe backend\carga.db. Generela primero con scripts\demo\02_carga_sqlite.ps1"
            exit 4
        }
        $env:RUTA_SQLITE = $CargaDb
        Escribir-Paso "Base de demostracion SQLite: backend\carga.db (no es la base real)."
    } else {
        $env:POSTGRES_DB = "quechua_wanka_demo"
        Escribir-Paso "Base de demostracion PostgreSQL: quechua_wanka_demo (cargela con 03_carga_postgres.ps1 si esta vacia)."
    }
} else {
    Escribir-Paso "Base de uso real ($Base)."
}

$ids = @()
Escribir-Paso "Arrancando el backend..."
$api = Start-Process -FilePath $Python -WindowStyle Minimized -PassThru -WorkingDirectory $Backend `
    -ArgumentList @("-m", "uvicorn", "infrastructure.main:app", "--app-dir", "src", "--host", "127.0.0.1", "--port", "$PuertoApi")
$ids += $api.Id

Escribir-Paso "Arrancando el frontend..."
$web = Start-Process -FilePath "cmd.exe" -WindowStyle Minimized -PassThru -WorkingDirectory $Frontend `
    -ArgumentList @("/c", "npm run dev -- --host 127.0.0.1 --port $PuertoWeb --strictPort")
$ids += $web.Id
Set-Content -LiteralPath $Pids -Value $ids

$segundos = Esperar-Estado
if ($null -eq $segundos) {
    Escribir-Error "La API no respondio 200 en /api/estado a tiempo. Revise las ventanas minimizadas."
    Detener-Servidores
    exit 5
}
Escribir-Ok "API lista en $segundos s: http://127.0.0.1:$PuertoApi/api/estado"

$web_ok = $false
for ($i = 0; $i -lt 30; $i++) {
    if (Puerto-Ocupado $PuertoWeb) { $web_ok = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $web_ok) { Escribir-Aviso "Vite aun no responde en el puerto $PuertoWeb." }

if (-not $SinNavegador) { Start-Process "http://127.0.0.1:$PuertoWeb" }
Escribir-Ok "Interfaz: http://127.0.0.1:$PuertoWeb  (para detener:  01_arrancar_app.ps1 -Detener)"
