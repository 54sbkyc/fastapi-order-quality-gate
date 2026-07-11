param(
    [switch]$CleanInstall,
    [switch]$UiSmoke,
    [switch]$LiveApi
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    $Python = "python"
}

function Invoke-Step($Name, [scriptblock]$Command) {
    Write-Host ""
    Write-Host "==> $Name"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name 失败，退出码：$LASTEXITCODE"
    }
    Write-Host "通过：$Name"
}

Set-Location $ProjectRoot

Write-Host "本地质量门禁开始"
Write-Host "项目目录：$ProjectRoot"

Invoke-Step "清理旧测试报告" {
    $AllureResults = Join-Path $ProjectRoot "allure-results"
    if (Test-Path -LiteralPath $AllureResults) {
        Remove-Item -LiteralPath $AllureResults -Recurse -Force
    }
    New-Item -ItemType Directory -Path $AllureResults | Out-Null
    $global:LASTEXITCODE = 0
}

Invoke-Step "Ruff 代码检查" {
    & $Python -m ruff check .
}

Invoke-Step "API 自动化测试 + 覆盖率门禁" {
    & $Python -m pytest tests/api --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=80 --alluredir=allure-results
}

Invoke-Step "Allure 报告元数据" {
    & $Python scripts/write_allure_metadata.py
}

Invoke-Step "生成前端质量快照" {
    & $Python scripts/build_quality_snapshot.py
}

Invoke-Step "测试套件质量检查" {
    & $Python -m pytest tests/meta -q
}

if ($LiveApi) {
    Invoke-Step "真实 HTTP API 黑盒测试" {
        & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ProjectRoot "scripts\api-e2e.ps1")
    }
}

Invoke-Step "前端依赖检查" {
    Push-Location (Join-Path $ProjectRoot "frontend")
    try {
        $HasNodeModules = Test-Path -LiteralPath "node_modules"
        $HasTypeScriptBin = Test-Path -LiteralPath "node_modules\.bin\tsc.cmd"
        if ($CleanInstall) {
            & npm.cmd ci
        } elseif (-not $HasNodeModules -or -not $HasTypeScriptBin) {
            & npm.cmd install
        } else {
            Write-Output "前端依赖已存在，跳过安装。需要干净安装时运行：.\scripts\quality-gate.ps1 -CleanInstall"
            $global:LASTEXITCODE = 0
        }
    } finally {
        Pop-Location
    }
}

Invoke-Step "前端生产构建" {
    Push-Location (Join-Path $ProjectRoot "frontend")
    try {
        & npm.cmd run build
    } finally {
        Pop-Location
    }
}

if ($UiSmoke) {
    Invoke-Step "Playwright UI 冒烟测试" {
        & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ProjectRoot "scripts\ui-smoke.ps1")
    }
}

Invoke-Step "质量报告摘要" {
    $PreviousPythonIoEncoding = $env:PYTHONIOENCODING
    $env:PYTHONIOENCODING = "utf-8"
    try {
        & $Python scripts/report-summary.py
    } finally {
        if ($null -eq $PreviousPythonIoEncoding) {
            Remove-Item Env:\PYTHONIOENCODING -ErrorAction SilentlyContinue
        } else {
            $env:PYTHONIOENCODING = $PreviousPythonIoEncoding
        }
    }
}

Write-Host ""
$CompletedLayers = @("lint", "进程内接口测试", "覆盖率", "meta 测试", "前端构建")
if ($LiveApi) {
    $CompletedLayers += "真实 HTTP API 测试"
}
if ($UiSmoke) {
    $CompletedLayers += "UI 冒烟测试"
}
Write-Host "本地质量门禁通过：$($CompletedLayers -join '、')。"
