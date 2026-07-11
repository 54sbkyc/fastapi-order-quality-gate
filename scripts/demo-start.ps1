$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RuntimeDir = Join-Path $ProjectRoot ".runtime"
$BackendLog = Join-Path $RuntimeDir "backend.out.log"
$BackendErrorLog = Join-Path $RuntimeDir "backend.err.log"
$FrontendLog = Join-Path $RuntimeDir "frontend.out.log"
$FrontendErrorLog = Join-Path $RuntimeDir "frontend.err.log"
$BackendPidFile = Join-Path $RuntimeDir "backend.pid"
$FrontendPidFile = Join-Path $RuntimeDir "frontend.pid"

function Write-Info($Message) {
    Write-Output "[demo-start] $Message"
}

function Resolve-Python {
    $LocalPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $LocalPython) {
        return $LocalPython
    }
    return "python"
}

function Test-Url($Url) {
    try {
        $Response = Invoke-WebRequest -Uri $Url -TimeoutSec 3 -UseBasicParsing
        return $Response.StatusCode -ge 200 -and $Response.StatusCode -lt 500
    } catch {
        return $false
    }
}

function Wait-Url($Url, $Name, $TimeoutSeconds) {
    $Deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $Deadline) {
        if (Test-Url $Url) {
            Write-Info "$Name is ready: $Url"
            return
        }
        Start-Sleep -Seconds 1
    }

    throw "$Name did not become ready in $TimeoutSeconds seconds: $Url"
}

New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null
Set-Location $ProjectRoot

$Python = Resolve-Python

Write-Info "Project root: $ProjectRoot"

if (Test-Url "http://127.0.0.1:8001/api/health") {
    Write-Info "Backend is already running."
} else {
    Write-Info "Starting FastAPI backend."
    Remove-Item -LiteralPath $BackendLog, $BackendErrorLog -Force -ErrorAction SilentlyContinue
    $BackendProcess = Start-Process `
        -FilePath $Python `
        -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001") `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $BackendLog `
        -RedirectStandardError $BackendErrorLog `
        -PassThru
    $BackendProcess.Id | Set-Content -LiteralPath $BackendPidFile -Encoding ASCII
}

Wait-Url "http://127.0.0.1:8001/api/health" "Backend health check" 30

if (Test-Url "http://127.0.0.1:5173") {
    Write-Info "Frontend is already running."
} else {
    Write-Info "Starting Vite frontend."
    Remove-Item -LiteralPath $FrontendLog, $FrontendErrorLog -Force -ErrorAction SilentlyContinue
    $FrontendProcess = Start-Process `
        -FilePath "npm.cmd" `
        -ArgumentList @("run", "dev") `
        -WorkingDirectory (Join-Path $ProjectRoot "frontend") `
        -RedirectStandardOutput $FrontendLog `
        -RedirectStandardError $FrontendErrorLog `
        -PassThru
    $FrontendProcess.Id | Set-Content -LiteralPath $FrontendPidFile -Encoding ASCII
}

Wait-Url "http://127.0.0.1:5173" "Frontend page" 45

Write-Output ""
Write-Output "Demo environment is ready:"
Write-Output "  Frontend: http://127.0.0.1:5173"
Write-Output "  Backend:  http://127.0.0.1:8001"
Write-Output "  Swagger:  http://127.0.0.1:8001/docs"
Write-Output "  Health:   http://127.0.0.1:8001/api/health"
Write-Output ""
Write-Output "Logs:"
Write-Output "  Backend stdout: $BackendLog"
Write-Output "  Backend stderr: $BackendErrorLog"
Write-Output "  Frontend stdout: $FrontendLog"
Write-Output "  Frontend stderr: $FrontendErrorLog"
Write-Output ""
Write-Output "Reset demo data before an interview: .\scripts\demo-reset.ps1"
