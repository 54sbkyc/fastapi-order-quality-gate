$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$FrontendRoot = Join-Path $ProjectRoot "frontend"

function Invoke-Step($Name, [scriptblock]$Command) {
    Write-Host ""
    Write-Host "==> $Name"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name 失败，退出码：$LASTEXITCODE"
    }
    Write-Host "通过：$Name"
}

function Set-BrowserExecutableIfAvailable {
    $Candidates = @(
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    )

    foreach ($Candidate in $Candidates) {
        if (Test-Path -LiteralPath $Candidate) {
            $env:PLAYWRIGHT_CHROME_EXECUTABLE_PATH = $Candidate
            Write-Host "使用本机浏览器：$Candidate"
            return
        }
    }

    Write-Host "未发现本机 Chrome/Edge，将使用 Playwright 自带 Chromium。"
    Write-Host "如果首次运行提示缺少浏览器，请执行：cd frontend; npx playwright install chromium"
}

Set-Location $ProjectRoot

Write-Host "UI 冒烟测试开始"
Write-Host "项目目录：$ProjectRoot"

Invoke-Step "检查前端 Playwright 依赖" {
    Push-Location $FrontendRoot
    try {
        if (-not (Test-Path -LiteralPath "node_modules\.bin\playwright.cmd")) {
            & npm.cmd install
        } else {
            Write-Output "Playwright 依赖已存在，跳过安装。"
            $global:LASTEXITCODE = 0
        }
    } finally {
        Pop-Location
    }
}

Invoke-Step "启动或复用演示环境" {
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ProjectRoot "scripts\demo-start.ps1")
}

Set-BrowserExecutableIfAvailable
$env:UI_SMOKE_BASE_URL = "http://127.0.0.1:5173"

try {
    Invoke-Step "运行 Playwright UI 冒烟用例" {
        Push-Location $FrontendRoot
        try {
            & npm.cmd run ui:smoke
        } finally {
            Pop-Location
        }
    }
} catch {
    Write-Host ""
    Write-Host "UI 冒烟测试失败，可查看以下产物："
    Write-Host "  HTML 报告：frontend\playwright-report\index.html"
    Write-Host "  截图/trace：frontend\test-results"
    throw
}

Write-Host ""
Write-Host "UI 冒烟测试通过：页面加载、API 状态、商品列表、注册登录、创建订单、订单展示和质量指标均已验证。"
