<#
.SYNOPSIS
  Đăng ký tác vụ Windows tự chạy scripts/update_daily_data.py mỗi ngày (TV5: cập nhật dữ liệu giá vàng định kỳ).
.EXAMPLE
  powershell -File scripts/schedule_daily_update.ps1                 # 07:30 mỗi ngày
  powershell -File scripts/schedule_daily_update.ps1 -Time 18:00
  powershell -File scripts/schedule_daily_update.ps1 -Remove         # gỡ tác vụ
Lưu ý: script ghi vào CSDL của TV5 và CSDL backend (xem DATABASE_URL); chỉ chạy khi đã sao lưu và nhóm đồng ý.
#>
param(
  [string]$Time = "07:30",
  [string]$TaskName = "GoldAI-DailyUpdate",
  [switch]$Remove
)
$ErrorActionPreference = "Stop"
if ($Remove) { schtasks /Delete /TN $TaskName /F; exit $LASTEXITCODE }
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Chưa có .venv tại $python" }
$cmd = "`"$python`" `"$root\scripts\update_daily_data.py`" --period 30d"
schtasks /Create /TN $TaskName /TR $cmd /SC DAILY /ST $Time /F
Write-Host "Đã đăng ký '$TaskName' chạy lúc $Time hằng ngày. Kiểm tra: schtasks /Query /TN $TaskName"
