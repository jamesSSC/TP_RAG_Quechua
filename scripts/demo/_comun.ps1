# Funciones comunes de los scripts de demostracion. Se cargan con:  . "$PSScriptRoot\_comun.ps1"
# Funciona con rutas con espacios: todas las rutas se pasan entre comillas o como argumentos.

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$script:Raiz     = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$script:Backend  = Join-Path $Raiz "backend"
$script:Frontend = Join-Path $Raiz "frontend"
$script:Python   = Join-Path $Backend ".venv\Scripts\python.exe"
$script:CargaDb  = Join-Path $Backend "carga.db"
$script:Evidencias = Join-Path $Raiz "docs\evidencias\cierre_u3\data_masiva"
$script:Pids     = Join-Path $PSScriptRoot ".pids"
$script:PuertoApi = 8000
$script:PuertoWeb = 5173

function Escribir-Paso([string]$Mensaje)  { Write-Host "[demo] $Mensaje" -ForegroundColor Cyan }
function Escribir-Ok([string]$Mensaje)    { Write-Host "[ ok ] $Mensaje" -ForegroundColor Green }
function Escribir-Aviso([string]$Mensaje) { Write-Host "[aviso] $Mensaje" -ForegroundColor Yellow }
function Escribir-Error([string]$Mensaje) { Write-Host "[error] $Mensaje" -ForegroundColor Red }

function Exigir-Python {
    if (-not (Test-Path -LiteralPath $Python)) {
        Escribir-Error "No existe el entorno virtual: $Python"
        Escribir-Error "Creelo desde backend/:  python -m venv .venv  y  pip install -r requirements.txt -r requirements-dev.txt"
        exit 2
    }
}

# Nombres de las variables de backend/.env, sin sus valores: las credenciales nunca se imprimen.
# Python las lee por su cuenta (pydantic); aqui solo se comprueba que el archivo exista.
function Comprobar-Env {
    if (-not (Test-Path -LiteralPath (Join-Path $Backend ".env"))) {
        Escribir-Aviso "No hay backend\.env: PostgreSQL usara los valores por defecto de la configuracion."
    }
}

function Puerto-Ocupado([int]$Puerto) {
    $c = New-Object System.Net.Sockets.TcpClient
    try { $c.Connect("127.0.0.1", $Puerto); return $true } catch { return $false } finally { $c.Close() }
}

function Estado-Api {
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$PuertoApi/api/estado" -TimeoutSec 30
        return $r.StatusCode
    } catch { return 0 }
}

function Esperar-Estado([int]$SegundosMax = 180) {
    $inicio = Get-Date
    while (((Get-Date) - $inicio).TotalSeconds -lt $SegundosMax) {
        if ((Estado-Api) -eq 200) { return [math]::Round(((Get-Date) - $inicio).TotalSeconds, 1) }
        Start-Sleep -Seconds 1
    }
    return $null
}

function Detener-Servidores {
    if (Test-Path -LiteralPath $Pids) {
        foreach ($linea in Get-Content -LiteralPath $Pids) {
            $id = 0
            if ([int]::TryParse($linea.Trim(), [ref]$id)) {
                # taskkill /T cierra tambien los procesos hijos (uvicorn, node/vite).
                & taskkill.exe /PID $id /T /F 2>$null | Out-Null
            }
        }
        Remove-Item -LiteralPath $Pids -Force
        Escribir-Ok "Servidores detenidos."
    } else {
        Escribir-Aviso "No hay servidores arrancados por estos scripts."
    }
}

# Quita de lo que se guarda las rutas propias del equipo (usuario, repositorio, carpeta temporal).
function Sanear-Linea([string]$Linea) {
    $tmp = [System.IO.Path]::GetTempPath().TrimEnd([char]92)
    foreach ($par in @(@($tmp, "<tmp>"), @($Raiz, "<repo>"), @($env:USERPROFILE, "<usuario>"))) {
        if ($par[0]) { $Linea = $Linea.Replace($par[0], $par[1]) }
    }
    # Variantes con nombre corto 8.3 (USER01~1) o con otro usuario
    return ($Linea -replace '(?i)[A-Z]:\\Users\\[^\\"]+\\AppData\\Local\\Temp', "<tmp>")
}

# Ejecuta un comando, muestra su salida y la guarda en $Archivo (UTF-8). Devuelve solo el codigo de salida.
function Ejecutar-Y-Guardar([string]$Archivo, [scriptblock]$Comando) {
    $dir = Split-Path -Parent $Archivo
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Set-Content -LiteralPath $Archivo -Value "" -Encoding UTF8
    # Lo que un programa externo escribe en stderr (logs de Python) no es un error de PowerShell.
    $anterior = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $Comando 2>&1 | ForEach-Object {
            $linea = Sanear-Linea "$_"
            Write-Host $linea
            Add-Content -LiteralPath $Archivo -Value $linea -Encoding UTF8
        }
        $codigo = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $anterior
    }
    return [int]$codigo
}
