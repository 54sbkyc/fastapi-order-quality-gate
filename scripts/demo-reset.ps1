$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RuntimeDir = Join-Path $ProjectRoot ".runtime"

function Write-Info($Message) {
    Write-Host "[演示复位] $Message"
}

function Assert-InProject($Path) {
    $FullPath = [System.IO.Path]::GetFullPath($Path)
    if (-not $FullPath.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "拒绝处理项目目录外的路径：$FullPath"
    }
    return $FullPath
}

function Stop-RecordedProcess($PidFile, $Label) {
    if (-not (Test-Path -LiteralPath $PidFile)) {
        return
    }

    try {
        $RawPid = (Get-Content -LiteralPath $PidFile -Encoding UTF8 -Raw).Trim()
        if ($RawPid.StartsWith("{")) {
            $Metadata = $RawPid | ConvertFrom-Json
            $ProcessId = [int]$Metadata.pid
        } else {
            $ProcessId = [int]$RawPid
        }
        $Process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($null -ne $Process) {
            Write-Info "停止由 demo-start.ps1 记录的 $Label 进程：PID $ProcessId"
            Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
        }
    } catch {
        Write-Info "跳过无法识别的 $Label PID 文件：$PidFile"
    }
}

function Stop-ProjectPort($Port, $Label) {
    $Connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($Connection in $Connections) {
        $Process = Get-CimInstance Win32_Process -Filter "ProcessId = $($Connection.OwningProcess)" -ErrorAction SilentlyContinue
        if ($null -eq $Process) {
            continue
        }

        $CommandLine = [string]$Process.CommandLine
        $LooksProjectRelated = (
            $CommandLine.Contains($ProjectRoot) -or
            $CommandLine.Contains("app.main:app") -or
            $CommandLine.Contains("uvicorn") -or
            ($Port -eq 8001 -and $Process.Name -like "python*") -or
            ($Port -eq 5173 -and $CommandLine.Contains("vite"))
        )

        if ($LooksProjectRelated) {
            Write-Info "停止占用 $Label 端口 $Port 的项目进程：PID $($Connection.OwningProcess)"
            Stop-Process -Id $Connection.OwningProcess -Force -ErrorAction SilentlyContinue
        } else {
            Write-Info "端口 $Port 被非本项目进程占用，已跳过：PID $($Connection.OwningProcess)"
        }
    }
}

function Remove-GeneratedPath($Path) {
    $FullPath = Assert-InProject $Path
    if (Test-Path -LiteralPath $FullPath) {
        for ($Attempt = 1; $Attempt -le 10; $Attempt++) {
            try {
                Remove-Item -LiteralPath $FullPath -Recurse -Force
                Write-Info "已清理：$FullPath"
                return
            } catch {
                if ($Attempt -eq 10) {
                    throw
                }
                Start-Sleep -Seconds 1
            }
        }
    }
}

Set-Location $ProjectRoot

Write-Info "项目目录：$ProjectRoot"

Stop-RecordedProcess (Join-Path $RuntimeDir "backend.pid") "后端"
Stop-RecordedProcess (Join-Path $RuntimeDir "frontend.pid") "前端"
Stop-RecordedProcess (Join-Path $RuntimeDir "backend.pid.json") "后端"
Stop-RecordedProcess (Join-Path $RuntimeDir "frontend.pid.json") "前端"
Stop-ProjectPort 8001 "后端"
Stop-ProjectPort 5173 "前端"
Start-Sleep -Seconds 2

Remove-GeneratedPath (Join-Path $ProjectRoot "order_quality_gate.db")
Remove-GeneratedPath (Join-Path $ProjectRoot ".coverage")
Remove-GeneratedPath (Join-Path $ProjectRoot "allure-results")
Remove-GeneratedPath (Join-Path $ProjectRoot "allure-report")
Remove-GeneratedPath $RuntimeDir

Write-Host ""
Write-Host "演示数据和本地运行产物已复位。"
Write-Host "重新启动演示环境：.\scripts\demo-start.ps1"
