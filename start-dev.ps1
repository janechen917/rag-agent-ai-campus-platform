# ============================================================
# 校园智慧学习平台 - 本地一键启动脚本 (Windows / PowerShell)
# 用法：在项目根目录执行  .\start-dev.ps1
# ============================================================

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "================================" -ForegroundColor Cyan
Write-Host " 启动 校园智慧学习平台 (dev)" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# ---------- 清理被占用的端口 ----------
Write-Host "`n[*] 清理被占用的端口 (3000 / 3001 / 8000) ..." -ForegroundColor Yellow
foreach ($port in 3000, 3001, 8000) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conns) {
        $conns | ForEach-Object {
            try {
                $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
                if ($proc) {
                    Write-Host "    杀掉端口 $port 上的 $($proc.ProcessName) (PID=$($proc.Id))" -ForegroundColor DarkGray
                    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
                }
            } catch {}
        }
    }
}

# ---------- 后端 ----------
$backendPath = Join-Path $root "backend"
$venvActivate = Join-Path $backendPath "venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvActivate)) {
    Write-Host "[!] 未找到 backend\venv，请先创建虚拟环境并安装依赖：" -ForegroundColor Yellow
    Write-Host "    cd backend; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt"
    exit 1
}

Write-Host "[1/2] 启动后端 Django (http://localhost:8000) ..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$backendPath'; .\venv\Scripts\Activate.ps1; python manage.py runserver"
)

# ---------- 前端 ----------
$frontendPath = Join-Path $root "frontend"
$nodeModules = Join-Path $frontendPath "node_modules"

if (-not (Test-Path $nodeModules)) {
    Write-Host "[!] 未找到 frontend\node_modules，请先执行：cd frontend; npm install" -ForegroundColor Yellow
    exit 1
}

Write-Host "[2/2] 启动前端 Vite (http://localhost:3000) ..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$frontendPath'; npm run dev"
)

Write-Host ""
Write-Host "已在新窗口分别启动前后端：" -ForegroundColor Cyan
Write-Host "  前端: http://localhost:3000"
Write-Host "  后端: http://localhost:8000"
Write-Host "  管理: http://localhost:8000/admin"
Write-Host ""
Write-Host "停止服务：在对应窗口按 Ctrl+C，或直接关闭窗口。" -ForegroundColor Yellow