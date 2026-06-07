# ============================================
# yt-dlp - Bilibili Batch Downloader
# ============================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = (Get-Item $ScriptDir).Parent.FullName
$ConfigFile = "$ProjectDir\config.yml"
$CookiesFile = "$ProjectDir\cookies.txt"
$ArchiveFile = "$ProjectDir\archive.txt"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Bilibili Batch Downloader (yt-dlp)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$env:PATH = "C:\myEnvironment\ffmpeg\ffmpeg-8.1.1-essentials_build\bin;$env:PATH"

$ytdlp = Get-Command yt-dlp -ErrorAction SilentlyContinue
if (-not $ytdlp) {
    Write-Host "[ERROR] yt-dlp not found. Run: pip install yt-dlp" -ForegroundColor Red
    pause
    exit 1
}

if (-not (Test-Path $CookiesFile)) {
    Write-Host "[WARN] Cookie file not found: $CookiesFile" -ForegroundColor Yellow
    Write-Host "[WARN] Will try to download without cookies" -ForegroundColor Yellow
}

if (-not (Test-Path $ConfigFile)) {
    Write-Host "[ERROR] Config file not found: $ConfigFile" -ForegroundColor Red
    pause
    exit 1
}

# Read config
$config = Get-Content $ConfigFile -Raw

# Parse download path
$DownloadPath = "./Downloaded"
$pathLine = $config -split "`n" | Where-Object { $_ -match '^\s*path:\s*(.+)$' }
if ($pathLine) {
    $pathValue = ($pathLine -split 'path:\s*', 2)[1].Trim()
    if ($pathValue) {
        $DownloadPath = $pathValue
    }
}

# Convert relative path to absolute path (relative to project root)
if (-not [System.IO.Path]::IsPathRooted($DownloadPath)) {
    $DownloadPath = Join-Path $ProjectDir $DownloadPath
}

# Check and create download directory
if (-not (Test-Path $DownloadPath)) {
    Write-Host "[INFO] Creating download directory: $DownloadPath" -ForegroundColor Yellow
    try {
        New-Item -ItemType Directory -Path $DownloadPath -Force | Out-Null
    } catch {
        Write-Host "[ERROR] Cannot create directory: $DownloadPath" -ForegroundColor Red
        Write-Host "[ERROR] $_" -ForegroundColor Red
        pause
        exit 1
    }
}

# Check write permission
try {
    $testFile = Join-Path $DownloadPath ".write_test_$(Get-Random)"
    [System.IO.File]::WriteAllText($testFile, "test")
    Remove-Item $testFile -Force
} catch {
    Write-Host "[ERROR] Cannot write to directory: $DownloadPath" -ForegroundColor Red
    Write-Host "[ERROR] $_" -ForegroundColor Red
    pause
    exit 1
}

# Parse links
$links = @()
$config -split "`n" | ForEach-Object {
    $line = $_.Trim()
    if ($line -match '^\s*-\s*(https?://\S+)') {
        $links += $Matches[1]
    }
}

if ($links.Count -eq 0) {
    Write-Host "[WARN] No links in config.yml" -ForegroundColor Yellow
    pause
    exit 0
}

Write-Host "Links count: $($links.Count)" -ForegroundColor DarkGray
Write-Host "Download directory: $DownloadPath" -ForegroundColor DarkGray
Write-Host ""

$totalFailed = 0

foreach ($link in $links) {
    Write-Host "---" -ForegroundColor DarkGray
    Write-Host "Processing: $link" -ForegroundColor White

    $outputTemplate = $DownloadPath + '/%(uploader)s/%(title)s.%(ext)s'
    $ytArgs = @(
        "-o", $outputTemplate,
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
Write-Host "  Download Complete" -ForegroundColor Cyan
if ($totalFailed -gt 0) {
    Write-Host "  Failed: $totalFailed links" -ForegroundColor Red
}
Write-Host "  Archive: $ArchiveFile" -ForegroundColor DarkGray
Write-Host "========================================" -ForegroundColor Cyan

if (Test-Path $DownloadPath) {
    explorer $DownloadPath
}
