"""
yt-dlp - Bilibili Batch Downloader (Python)
读取 config.yml 中的链接，批量调用 yt-dlp 下载 B 站视频。
"""
import subprocess
import sys
import shutil
from pathlib import Path
from datetime import datetime

import yaml


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_DIR / "config.yml"
# 默认值（相对路径，会在运行时转为绝对路径）
DEFAULT_COOKIES = PROJECT_DIR / "cookies.txt"
DEFAULT_ARCHIVE = PROJECT_DIR / "archive.txt"


def print_header():
    print("=" * 40)
    print("  Bilibili Batch Downloader (yt-dlp)")
    print("=" * 40)


def check_ytdlp():
    if shutil.which("yt-dlp") is None:
        print("[ERROR] yt-dlp not found. Run: pip install yt-dlp")
        sys.exit(1)


def check_and_create_directory(download_path):
    """检查并创建下载目录，确保可写"""
    path = Path(download_path)

    # 如果是相对路径，转换为绝对路径（相对于项目根目录）
    if not path.is_absolute():
        path = PROJECT_DIR / path

    # 创建目录（如果不存在）
    if not path.exists():
        print(f"[INFO] Creating download directory: {path}")
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[ERROR] Cannot create directory: {path}")
            print(f"[ERROR] {e}")
            sys.exit(1)

    # 检查写入权限
    try:
        test_file = path / f".write_test_{__import__('random').random()}"
        test_file.write_text("test")
        test_file.unlink()
    except Exception as e:
        print(f"[ERROR] Cannot write to directory: {path}")
        print(f"[ERROR] {e}")
        sys.exit(1)

    # 返回绝对路径
    return str(path)


def load_config():
    if not CONFIG_FILE.exists():
        print(f"[ERROR] Config file not found: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    links = config.get("link", []) if config else []
    download_path = config.get("path") if config else None

    if not download_path:
        print("[ERROR] 'path' not configured in config.yml")
        sys.exit(1)

    # 从配置读取 cookies 和 archive 路径，转换为绝对路径
    cookies_path = config.get("cookies_file", "cookies.txt") if config else "cookies.txt"
    archive_path = config.get("archive_file", "archive.txt") if config else "archive.txt"

    if not Path(cookies_path).is_absolute():
        cookies_path = PROJECT_DIR / cookies_path
    if not Path(archive_path).is_absolute():
        archive_path = PROJECT_DIR / archive_path

    return links, download_path, cookies_path, archive_path


def check_cookie_validity(cookies_file):
    """检查 cookie 是否过期，重点检查 SESSDATA 等认证 Cookie"""
    if not cookies_file.exists():
        return None, "[WARN] Cookie file not found"

    try:
        with open(cookies_file, "r", encoding="utf-8") as f:
            content = f.read()

        now = datetime.now()
        auth_cookies = {}

        for line in content.split("\n"):
            if line.strip() and not line.startswith("#"):
                parts = line.split("\t")
                if len(parts) >= 6:
                    name = parts[5].strip()
                    try:
                        expiry_timestamp = int(parts[4])
                        if expiry_timestamp > 0:
                            expires = datetime.fromtimestamp(expiry_timestamp)
                            auth_cookies[name] = expires
                    except ValueError:
                        continue

        if not auth_cookies:
            return None, "[WARN] Cannot parse cookie expiry time"

        critical_cookies = ["SESSDATA", "bili_jct", "DedeUserID"]
        expired_cookies = []
        expiring_soon = []

        for name, expires in auth_cookies.items():
            if name in critical_cookies:
                if now > expires:
                    expired_cookies.append(f"{name} ({expires.strftime('%Y-%m-%d')})")
                elif (expires - now).days < 1:
                    expiring_soon.append(name)

        if expired_cookies:
            return False, f"[ERROR] Auth cookies expired: {', '.join(expired_cookies)}"

        if expiring_soon:
            return True, f"[WARN] Cookies expire soon: {', '.join(expiring_soon)}"

        sessdata_expiry = auth_cookies.get("SESSDATA")
        if sessdata_expiry:
            days_left = (sessdata_expiry - now).days
            return True, f"[INFO] Cookie valid until {sessdata_expiry.strftime('%Y-%m-%d %H:%M:%S')} ({days_left} days left)"
        else:
            return None, "[WARN] SESSDATA not found in cookies"

    except Exception as e:
        return None, f"[WARN] Error checking cookie: {e}"


def build_args(link, download_path, cookies_file, archive_file):
    output_template = f"{download_path}/%(uploader)s/%(title)s.%(ext)s"
    args = [
        "yt-dlp",
        "-o", output_template,
        "-f", "bestvideo+bestaudio",
        "--merge-output-format", "mp4",
        "--download-archive", str(archive_file),
    ]

    if "space.bilibili.com" not in link:
        args.append("--no-playlist")

    if cookies_file.exists():
        args.extend(["--cookies", str(cookies_file)])

    args.append(link)
    return args


def main():
    print_header()
    check_ytdlp()

    links, download_path, cookies_path, archive_path = load_config()

    # 检查下载目录，返回绝对路径
    download_path = check_and_create_directory(download_path)

    if not cookies_path.exists():
        print(f"[WARN] Cookie file not found: {cookies_path}")
        print("[WARN] Will try to download without cookies")
    else:
        is_valid, msg = check_cookie_validity(cookies_path)
        print(msg)
        if is_valid is False:
            print("[ERROR] Please refresh cookies: python scripts/refresh_cookies.py")
            sys.exit(1)

    if not links:
        print("[WARN] No links in config.yml")
        return

    print(f"Links count: {len(links)}")
    print(f"Download directory: {download_path}")
    print()

    failed = []

    for i, link in enumerate(links, 1):
        print("-" * 40)
        print(f"[{i}/{len(links)}] {link}")

        args = build_args(link, download_path, cookies_path, archive_path)
        result = subprocess.run(args)

        if result.returncode == 0:
            print("  [OK]")
        else:
            print(f"  [FAIL] exit code: {result.returncode}")
            failed.append((link, result.returncode))

    print()
    print("=" * 40)
    print("  Download Complete")
    if failed:
        print(f"  Failed: {len(failed)} links")
        for link, code in failed:
            print(f"    [{code}] {link}")
    print(f"  Archive: {archive_path}")
    print("=" * 40)


if __name__ == "__main__":
    main()
