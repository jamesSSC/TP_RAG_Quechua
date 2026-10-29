# Corre todas las verificaciones y deja un resumen de una pantalla:
# pytest, vitest, arnes de 248 consultas, entrenar_predictores, evaluar_pmv2, Newman y pip-audit.
#
# - entrenar_predictores se ejecuta con QW_MODELOS_SALIDA apuntando a una carpeta temporal: nunca
#   sobrescribe los modelos versionados de backend\modelos.
# - Newman necesita la API: si no esta levantada, este script la arranca (SQLite temporal) y la detiene al final.
param(
    [string]$Salida = (Join-Path (Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path "docs\evidencias\cierre_u3\data_masiva") "metricas")
)
. "$PSScriptRoot\_comun.ps1"
Exigir-Python

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("qw_metricas_" + [guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
New-Item -ItemType Directory -Path $Salida -Force | Out-Null
$resumen = New-Object System.Collections.ArrayList

function Registrar([string]$Nombre, [bool]$Ok, [string]$Detalle) {
    [void]$resumen.Add([pscustomobject]@{ Verificacion = $Nombre; Estado = $(if ($Ok) { "OK" } else { "FALLA" }); Detalle = $Detalle })
}
function Ultima-Linea([string]$Archivo, [string]$Patron) {
    $l = Get-Content -LiteralPath $Archivo -Encoding UTF8 | Where-Object { $_ -match $Patron } | Select-Object -Last 1
    if ($l) { return ($l -replace '\x1b\[[0-9;]*m', '').Trim() } else { return "sin dato" }
}

$modelosAntes = (& git -C $Raiz status --porcelain -- backend/modelos) -join ""
Push-Location -LiteralPath $Backend
try {
    # 1) pytest
    Escribir-Paso "pytest ..."
    $f = Join-Path $Salida "pytest.txt"
    $c = Ejecutar-Y-Guardar $f { & $Python -m pytest -q }
    Registrar "pytest" ($c -eq 0) (Ultima-Linea $f '(passed|failed|error)')

    # 3) arnes de 248 consultas, comparado con la linea base congelada
    Escribir-Paso "arnes de 248 consultas ..."
    $arn = Join-Path $tmp "arnes"
    $f = Join-Path $Salida "arnes.txt"
    $c = Ejecutar-Y-Guardar $f { & $Python "scripts\arnes_linea_base.py" "$arn" }
    $base = Join-Path $Raiz "docs\evidencias\cierre_u3\00_linea_base_2980a81\arnes"
    $detalle = "salida generada"
    $ok = ($c -eq 0)
    if ($ok -and (Test-Path -LiteralPath $base)) {
        $iguales = $true
        foreach ($n in @("arnes_por_consulta.csv", "barrido_umbral.csv")) {
            $a = (Get-Content -LiteralPath (Join-Path $arn $n) -Raw) -replace "`r", ""
            $b = (Get-Content -LiteralPath (Join-Path $base $n) -Raw) -replace "`r", ""
            if ($a -ne $b) { $iguales = $false }
        }
        $ok = $iguales
        $detalle = $(if ($iguales) { "identico a la linea base 2980a81" } else { "DIFIERE de la linea base" })
    } elseif ($ok) { $detalle = "sin linea base local para comparar" }
    Registrar "arnes (A, B, C, D)" $ok $detalle

    # 4) entrenar_predictores sobre una copia temporal
    Escribir-Paso "entrenar_predictores (modelos en carpeta temporal) ..."
    $modTmp = Join-Path $tmp "modelos"
    New-Item -ItemType Directory -Path $modTmp -Force | Out-Null
    $env:QW_MODELOS_SALIDA = $modTmp
    $f = Join-Path $Salida "entrenar_predictores.txt"
    $c = Ejecutar-Y-Guardar $f { & $Python "scripts\entrenar_predictores.py" (Join-Path $tmp "entrenamiento") }
    Remove-Item Env:\QW_MODELOS_SALIDA -ErrorAction SilentlyContinue
    $modelosDespues = (& git -C $Raiz status --porcelain -- backend/modelos) -join ""
    $intactos = ($modelosAntes -eq $modelosDespues)
    Registrar "entrenar_predictores" (($c -eq 0) -and $intactos) $(if ($intactos) { "modelos versionados intactos" } else { "OJO: cambiaron los modelos versionados" })

    # 5) evaluar_pmv2
    Escribir-Paso "evaluar_pmv2 ..."
    $pm = Join-Path $tmp "pmv2"
    $f = Join-Path $Salida "evaluar_pmv2.txt"
    $c = Ejecutar-Y-Guardar $f { & $Python "scripts\evaluar_pmv2.py" "$pm" }
    $ok = ($c -eq 0)
    $detalle = "sin dato"
    $json = Join-Path $pm "no_regresion_pmv2.json"
    if (Test-Path -LiteralPath $json) {
        $j = Get-Content -LiteralPath $json -Raw -Encoding UTF8 | ConvertFrom-Json
        $rn06 = $j.rn06_respuestas_pmv2_subconjunto_de_pmv1
        $ok = $ok -and ($rn06 -eq $true) -and ($j.fp_C_pmv2 -eq 0)
        $detalle = "RN-06 = $rn06; falsos positivos en C = $($j.fp_C_pmv2)"
    }
    Registrar "evaluar_pmv2" $ok $detalle
} finally {
    Pop-Location
}

# 2) vitest
Escribir-Paso "vitest ..."
Push-Location -LiteralPath $Frontend
try {
    $f = Join-Path $Salida "vitest.txt"
    $c = Ejecutar-Y-Guardar $f { & cmd.exe /c "npx vitest run" }
    Registrar "vitest" ($c -eq 0) (Ultima-Linea $f '^\s*Tests\s')
} finally {
    Pop-Location
}

# 6) Newman contra la API (la arranca si hace falta)
Escribir-Paso "Newman ..."
$arrancada = $null
$envAntes = @{ B = $env:BASE_DATOS; R = $env:RUTA_SQLITE }
if ((Estado-Api) -ne 200) {
    if (Puerto-Ocupado $PuertoApi) {
        Registrar "Newman" $false "el puerto $PuertoApi esta ocupado por otro programa"
    } else {
        $env:BASE_DATOS = "sqlite"
        $env:RUTA_SQLITE = Join-Path $tmp "newman.db"
        $arrancada = Start-Process -FilePath $Python -WindowStyle Hidden -PassThru -WorkingDirectory $Backend `
            -ArgumentList @("-m", "uvicorn", "infrastructure.main:app", "--app-dir", "src", "--host", "127.0.0.1", "--port", "$PuertoApi")
        if ($null -eq (Esperar-Estado)) { Registrar "Newman" $false "la API no arranco" ; $arrancada = $arrancada }
    }
}
if ((Estado-Api) -eq 200) {
    $coleccion = Join-Path $Raiz "docs\Asistente_Quechua_Wanka.postman_collection.json"
    # El informe JSON de Newman contiene las respuestas completas (texto del corpus): va a la carpeta temporal.
    $informe = Join-Path $tmp "newman.json"
    $f = Join-Path $Salida "newman.txt"
    $c = Ejecutar-Y-Guardar $f { & cmd.exe /c "npx --yes newman run `"$coleccion`" --env-var base_url=http://127.0.0.1:$PuertoApi --reporters cli,json --reporter-json-export `"$informe`" --color off" }
    $detalle = "sin informe"
    if (Test-Path -LiteralPath $informe) {
        $s = (Get-Content -LiteralPath $informe -Raw -Encoding UTF8 | ConvertFrom-Json).run.stats
        $detalle = "solicitudes $($s.requests.total) (fallidas $($s.requests.failed)) - afirmaciones $($s.assertions.total) (fallidas $($s.assertions.failed))"
    }
    Registrar "Newman" ($c -eq 0) $detalle
}
if ($arrancada) { & taskkill.exe /PID $arrancada.Id /T /F 2>$null | Out-Null; Escribir-Ok "API temporal detenida." }
$env:BASE_DATOS = $envAntes.B; $env:RUTA_SQLITE = $envAntes.R
if (-not $envAntes.B) { Remove-Item Env:\BASE_DATOS -ErrorAction SilentlyContinue }
if (-not $envAntes.R) { Remove-Item Env:\RUTA_SQLITE -ErrorAction SilentlyContinue }

# 7) pip-audit
Escribir-Paso "pip-audit ..."
Push-Location -LiteralPath $Backend
try {
    $f = Join-Path $Salida "pip_audit.txt"
    $c = Ejecutar-Y-Guardar $f { & $Python -m pip_audit -r requirements.txt }
    Registrar "pip-audit" ($c -eq 0) (Ultima-Linea $f '(No known|vulnerab)')
} finally {
    Pop-Location
}

# --- Resumen de una pantalla ---
$linea = "=" * 78
$texto = @($linea, "  RESUMEN DE METRICAS  -  $(Get-Date -Format 'yyyy-MM-dd HH:mm')", $linea)
foreach ($r in $resumen) { $texto += ("  {0,-22} {1,-6} {2}" -f $r.Verificacion, $r.Estado, $r.Detalle) }
$fallas = @($resumen | Where-Object { $_.Estado -ne "OK" }).Count
$texto += $linea
$texto += $(if ($fallas -eq 0) { "  TODO EN VERDE" } else { "  $fallas verificacion(es) con FALLA: revise los archivos en $Salida" })
$texto += $linea
$texto | ForEach-Object { Write-Host $_ }
$texto | Set-Content -LiteralPath (Join-Path $Salida "resumen.txt") -Encoding UTF8

Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
exit $(if ($fallas -eq 0) { 0 } else { 1 })
