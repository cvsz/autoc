param(
    [string]$Python = "python",
    [string]$DistPath = "dist\windows",
    [string]$WorkPath = "build\windows"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & $Python -m venv .venv
}

& ".venv\Scripts\python.exe" -m pip install -e ".[build]"

New-Item -ItemType Directory -Force -Path $DistPath | Out-Null
New-Item -ItemType Directory -Force -Path $WorkPath | Out-Null

& ".venv\Scripts\python.exe" -m PyInstaller `
    --noconfirm `
    --clean `
    --distpath $DistPath `
    --workpath $WorkPath `
    "windows\ggtmoni-gui.spec"

Copy-Item ".env.example" (Join-Path $DistPath ".env.example") -Force

$zipPath = Join-Path (Split-Path $DistPath -Parent) "ggtmoni-windows11-gui.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}
$archiveItems = Get-ChildItem -Force -Path $DistPath | ForEach-Object { $_.FullName }
Compress-Archive -Path $archiveItems -DestinationPath $zipPath -Force
