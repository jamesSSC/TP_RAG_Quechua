# Carga HTTP de POST /api/consultas con Locust: 1, 5 y 10 usuarios durante 60 s cada uno.
# La API corre con GENERADOR=literal (mide la API, no la GPU) y ORIGEN_CONSULTAS=carga sobre una base
# TEMPORAL aparte: la base real nunca se usa. Resultados en docs\evidencias\cierre_u3\b10_carga\.
param(
    [int[]]$Usuarios = @(1, 5, 10),
    [int]$Segundos = 60,
    [int]$Puerto = 8003,
    [string]$Salida = (Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path "docs\evidencias\cierre_u3\b10_carga")
)
. "$PSScriptRoot\_comun.ps1"
$ErrorActionPreference = "Continue"   # el log de Locust sale por stderr y no es un error
Exigir-Python
New-Item -ItemType Directory -Path $Salida -Force | Out-Null

if (Puerto-Ocupado $Puerto) { Escribir-Error "El puerto $Puerto esta ocupado."; exit 3 }
$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("qw_carga_" + [guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
$env:BASE_DATOS = "sqlite"
$env:RUTA_SQLITE = Join-Path $tmp "carga_http.db"
$env:CARPETA_DATOS = Join-Path $tmp "datos"
$env:GENERADOR = "literal"
$env:ORIGEN_CONSULTAS = "carga"

Escribir-Paso "Arrancando la API (generador literal, origen carga, base temporal) en 127.0.0.1:$Puerto ..."
$api = Start-Process -FilePath $Python -WindowStyle Hidden -PassThru -WorkingDirectory $Backend `
    -ArgumentList @("-m", "uvicorn", "infrastructure.main:app", "--app-dir", "src", "--host", "127.0.0.1", "--port", "$Puerto")
try {
    $listo = $false
    for ($i = 0; $i -lt 90; $i++) {
        try { if ((Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$Puerto/api/estado" -TimeoutSec 30).StatusCode -eq 200) { $listo = $true; break } } catch { Start-Sleep 1 }
    }
    if (-not $listo) { Escribir-Error "La API no respondio."; exit 5 }

    foreach ($u in $Usuarios) {
        Escribir-Paso "Locust: $u usuario(s) durante $Segundos s ..."
        Push-Location -LiteralPath $Backend
        try {
            & $Python -m locust -f "scripts\carga\locustfile.py" --headless -u $u -r $u -t "${Segundos}s" `
                --host "http://127.0.0.1:$Puerto" --csv (Join-Path $Salida "locust_${u}_usuarios") --only-summary 2>&1 |
                ForEach-Object { Write-Host "$_" }
        } finally { Pop-Location }
    }
    # La analitica de demanda real no debe contar nada de esto
    $d = Invoke-RestMethod "http://127.0.0.1:$Puerto/api/analitica/demanda" -TimeoutSec 60
    $d | ConvertTo-Json -Depth 5 | Out-Null
    Set-Content -LiteralPath (Join-Path $Salida "analitica_tras_la_carga.json") -Encoding UTF8 -Value (
        @{ por_origen = $d.por_origen; consultas_contadas_como_demanda_real = $d.estadisticas.total; suficiente = $d.suficiente; modo = $d.modo } | ConvertTo-Json)
} finally {
    & taskkill.exe /PID $api.Id /T /F 2>$null | Out-Null
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
Escribir-Ok "Listo. Resultados en $Salida"
