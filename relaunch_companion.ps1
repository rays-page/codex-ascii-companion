param(
    [switch]$Debug
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path $scriptDir "codex_ascii_companion.pyw"
$pythonw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source

if (-not $pythonw) {
    $localPythonRoot = Join-Path $env:LOCALAPPDATA "Python"
    if (Test-Path -LiteralPath $localPythonRoot) {
        $pythonw = Get-ChildItem -Path $localPythonRoot -Recurse -Filter pythonw.exe -ErrorAction SilentlyContinue |
            Select-Object -First 1 -ExpandProperty FullName
    }
}

if (-not $pythonw) {
    throw "pythonw.exe was not found. Install Python or add pythonw.exe to PATH before using the relaunch helper."
}

Get-CimInstance Win32_Process |
    Where-Object { $_.Name -eq "pythonw.exe" -and $_.CommandLine -like "*$scriptPath*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

$arguments = @($scriptPath)
if ($Debug) {
    $arguments += "--debug"
}

$process = Start-Process -FilePath $pythonw -ArgumentList $arguments -PassThru
Write-Output "Restarted Codex Courier Pod (PID $($process.Id))."
