# Builds P3_Thunder_Link.pdf from report.html using Microsoft Edge (installed on every Windows 11 PC).
# Run from anywhere:  powershell -ExecutionPolicy Bypass -File docs\reports\p3\build.ps1
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$html = Join-Path $here 'report.html'
$pdf = Join-Path $here 'P3_Thunder_Link.pdf'
$edge = @(
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw 'Microsoft Edge not found. Open report.html in a browser and use Print > Save as PDF instead.' }

$url = 'file:///' + ($html -replace '\\', '/')
$profile = Join-Path $env:TEMP 'p3-report-edge-profile'
& $edge --headless --disable-gpu --no-pdf-header-footer --user-data-dir="$profile" --print-to-pdf="$pdf" $url | Out-Null
Start-Sleep -Seconds 2
if (Test-Path $pdf) { "Built $pdf" } else { throw 'PDF was not created.' }
