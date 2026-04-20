param(
    [switch]$Debug
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path $scriptDir "codex_ascii_companion.pyw"
$preferredPythonw = "C:\Users\raymo_w9whwcn\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"

if (Test-Path -LiteralPath $preferredPythonw) {
    $pythonw = $preferredPythonw
} else {
    $pythonw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
    if (-not $pythonw) {
        throw "pythonw.exe was not found. Update relaunch_companion.ps1 with the correct interpreter path."
    }
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
