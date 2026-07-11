param(
    [string]$BaseUrl = "",
    [double]$TimeoutSeconds = 10,
    [ValidateSet("e2e", "smoke", "regression")]
    [string]$Marker = "e2e"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RuntimeDir = Join-Path $ProjectRoot ".runtime"
$ResultDir = Join-Path $ProjectRoot "allure-e2e-results"
$BackendLog = Join-Path $RuntimeDir "api-e2e-backend.out.log"
$BackendErrorLog = Join-Path $RuntimeDir "api-e2e-backend.err.log"
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}
if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
    $BaseUrl = if ($env:API_BASE_URL) { $env:API_BASE_URL } else { "http://127.0.0.1:8001" }
}

$BaseUrl = $BaseUrl.TrimEnd("/")
$ApiUri = [System.Uri]$BaseUrl
$IsLocalTarget = $ApiUri.Host -in @("127.0.0.1", "localhost", "::1")
$StartedProcess = $null

function Test-ApiHealth {
    $PreviousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    & $Python -c "import os,sys,httpx; trust=os.getenv('API_TRUST_ENV','false').lower()=='true'; r=httpx.get(os.environ['API_BASE_URL'] + '/api/health', timeout=3, trust_env=trust); sys.exit(0 if r.status_code == 200 else 1)" *> $null
    $HealthExitCode = $LASTEXITCODE
    $ErrorActionPreference = $PreviousErrorActionPreference
    return $HealthExitCode -eq 0
}

function Wait-ApiHealth([int]$Timeout) {
    $Deadline = (Get-Date).AddSeconds($Timeout)
    while ((Get-Date) -lt $Deadline) {
        if (Test-ApiHealth) {
            return
        }
        Start-Sleep -Seconds 1
    }
    throw "API 在 $Timeout 秒内未就绪：$BaseUrl"
}

Set-Location $ProjectRoot
New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null
$env:API_BASE_URL = $BaseUrl
$env:API_TIMEOUT_SECONDS = [string]$TimeoutSeconds
if (-not $env:API_TRUST_ENV) {
    $env:API_TRUST_ENV = "false"
}

if (-not (Test-ApiHealth)) {
    if (-not $IsLocalTarget) {
        throw "远程测试环境健康检查失败，不会自动启动本地服务：$BaseUrl"
    }

    Remove-Item -LiteralPath $BackendLog, $BackendErrorLog -Force -ErrorAction SilentlyContinue
    $Port = if ($ApiUri.IsDefaultPort) { 80 } else { $ApiUri.Port }
    Write-Host "启动本地 FastAPI：$BaseUrl"
    $StartedProcess = Start-Process `
        -FilePath $Python `
        -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", $Port) `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $BackendLog `
        -RedirectStandardError $BackendErrorLog `
        -WindowStyle Hidden `
        -PassThru
    Wait-ApiHealth 30
} else {
    Write-Host "复用已运行的 API：$BaseUrl"
}

if (Test-Path -LiteralPath $ResultDir) {
    Remove-Item -LiteralPath $ResultDir -Recurse -Force
}
New-Item -ItemType Directory -Path $ResultDir | Out-Null

try {
    Write-Host "运行真实 HTTP API 测试：$BaseUrl，marker=$Marker"
    & $Python -m pytest tests/e2e -m $Marker --alluredir=allure-e2e-results
    $TestExitCode = $LASTEXITCODE
} finally {
    if ($null -ne $StartedProcess -and -not $StartedProcess.HasExited) {
        Stop-Process -Id $StartedProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "已停止脚本启动的本地 FastAPI：PID $($StartedProcess.Id)"
    }
}

if ($TestExitCode -ne 0) {
    Write-Host "后端日志：$BackendLog"
    Write-Host "后端错误日志：$BackendErrorLog"
    exit $TestExitCode
}

Write-Host "真实 HTTP API 测试通过，Allure 结果：$ResultDir"
