# ============================================
# yt-dlp
# ============================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = (Get-Item $ScriptDir).Parent.FullName
$ConfigFile = "$ProjectDir\config.yml"
$CookiesFile = "$ProjectDir\cookies.txt"
$ArchiveFile = "$ProjectDir\archive.txt"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  哔哩哔哩批量下载器 (yt-dlp)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$env:PATH = "C:\myEnvironment\ffmpeg\ffmpeg-8.1.1-essentials_build\bin;$env:PATH"

$ytdlp = Get-Command yt-dlp -ErrorAction SilentlyContinue
if (-not $ytdlp) {
    Write-Host "[ERROR] yt-dlp not found. Run: pip install yt-dlp" -ForegroundColor Red
    pause
    exit 1
}

if (-not (Test-Path $CookiesFile)) {
    Write-Host "[WARN] Cookie文件不存在: $CookiesFile" -ForegroundColor Yellow
    Write-Host "[WARN] 将尝试无Cookie下载" -ForegroundColor Yellow
}

if (-not (Test-Path $ConfigFile)) {
    Write-Host "[ERROR] 配置文件不存在: $ConfigFile" -ForegroundColor Red
    pause
    exit 1
}

$config = Get-Content $ConfigFile -Raw

$links = @()
$config -split "`n" | ForEach-Object {
    $line = $_.Trim()
    if ($line -match '^\s*-\s*(https?://\S+)') {
        $links += $Matches[1]
    }
}

if ($links.Count -eq 0) {
    Write-Host "[WARN] config.yml 中没有链接" -ForegroundColor Yellow
    pause
    exit 0
}

$startTime = ""
$endTime = ""
if ($config -match 'start_time:\s*"([^"]*)"') { $startTime = $Matches[1] }
if ($config -match 'end_time:\s*"([^"]*)"') { $endTime = $Matches[1] }

$downloadPath = "C:\Users\sb\Desktop\0需处理-C盘\B站下载\Downloaded"
if ($config -match 'path:\s*(.+?)\s*$') {
    $rawPath = $Matches[1].Trim()
    if ($rawPath -and $rawPath -ne '""') { $downloadPath = $rawPath }
}

Write-Host "链接数: $($links.Count)" -ForegroundColor DarkGray
Write-Host "下载目录: $downloadPath" -ForegroundColor DarkGray
if ($startTime) { Write-Host "时间过滤: >= $startTime" -ForegroundColor DarkGray }
if ($endTime) { Write-Host "时间过滤: <= $endTime" -ForegroundColor DarkGray }
Write-Host ""

$totalFailed = 0

foreach ($link in $links) {
    Write-Host "---" -ForegroundColor DarkGray
    Write-Host "处理: $link" -ForegroundColor White

    $ytArgs = @(
        "-o", "$downloadPath/%(uploader)s/%(title)s.%(ext)s",
        "-f", "bestvideo+bestaudio",
        "--merge-output-format", "mp4",
        "--download-archive", $ArchiveFile
    )

    if ($link -notmatch "space\.bilibili\.com") {
        $ytArgs += "--no-playlist"
    }

    if (Test-Path $CookiesFile) {
        $ytArgs += "--cookies"
        $ytArgs += $CookiesFile
    }

    if ($startTime) {
        $ytArgs += "--dateafter"
        $ytArgs += $startTime
    }
    if ($endTime) {
        $ytArgs += "--datebefore"
        $ytArgs += $endTime
    }

    $ytArgs += $link

    & yt-dlp $ytArgs
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Host "  [OK]" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] exit code: $exitCode" -ForegroundColor Red
        $totalFailed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  下载完成" -ForegroundColor Cyan
if ($totalFailed -gt 0) {
    Write-Host "  失败: $totalFailed 个链接" -ForegroundColor Red
}
Write-Host "  增量记录: $ArchiveFile" -ForegroundColor DarkGray
Write-Host "========================================" -ForegroundColor Cyan

if (Test-Path $downloadPath) {
    explorer $downloadPath
}