"""
yt-dlp - Bilibili Batch Downloader (Python)
读取 config.yml 中的链接，批量调用 yt-dlp 下载 B 站视频。
"""
import random
import subprocess
import sys
import shutil
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from typing import List, Tuple, Dict, Optional, Any

import yaml

from utils import PROJECT_DIR, CONFIG_FILE, COOKIES_PATH, ARCHIVE_PATH, CRITICAL_COOKIES


class DownloaderError(Exception):
    exit_code: int = 1


class ConfigError(DownloaderError):
    exit_code: int = 2


class SecurityError(DownloaderError):
    exit_code: int = 3


class DownloaderRuntimeError(DownloaderError):
    exit_code: int = 4


def print_header() -> None:
    print("=" * 40)
    print("  Bilibili Batch Downloader (yt-dlp)")
    print("=" * 40)


def check_ytdlp() -> None:
    if shutil.which("yt-dlp") is None:
        raise DownloaderRuntimeError("yt-dlp not found. Run: pip install yt-dlp")


def validate_and_normalize_path(download_path: str) -> Path:
    path = Path(download_path)

    if not path.is_absolute():
        path = PROJECT_DIR / path

    resolved_path = path.resolve()

    try:
        resolved_path.relative_to(PROJECT_DIR)
    except ValueError:
        raise SecurityError(f"Download path is outside project directory: {resolved_path}")

    return resolved_path


def validate_url(link: str) -> bool:
    try:
        parsed = urlparse(link)
        if parsed.scheme not in ("http", "https"):
            raise SecurityError(f"Invalid URL scheme: {parsed.scheme}. Only http/https are allowed")
        if not parsed.netloc:
            raise SecurityError("Invalid URL: missing host")
        allowed_domains = ["bilibili.com", "b23.tv"]
        if not any(domain in parsed.netloc for domain in allowed_domains):
            raise SecurityError(f"URL not from allowed domains: {parsed.netloc}. Only {allowed_domains} are allowed")
        return True
    except Exception as e:
        raise SecurityError(f"Invalid URL: {link}. {e}")


def check_and_create_directory(download_path: str) -> Path:
    path = validate_and_normalize_path(download_path)

    if not path.exists():
        print(f"[INFO] Creating download directory: {path}")
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise DownloaderRuntimeError(f"Cannot create directory: {path}. {e}")

    try:
        test_file = path / f".write_test_{random.random()}"
        test_file.write_text("test")
        test_file.unlink()
    except Exception as e:
        raise DownloaderRuntimeError(f"Cannot write to directory: {path}. {e}")

    return path


def load_config() -> Tuple[List[str], str, Path, Path]:
    if not CONFIG_FILE.exists():
        raise ConfigError(f"Config file not found: {CONFIG_FILE}")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config: Dict[str, Any] = yaml.safe_load(f) or {}

    links: List[str] = config.get("link", [])
    download_path: Optional[str] = config.get("path")

    if not download_path:
        raise ConfigError("'path' not configured in config.yml")

    cookies_path: Path = Path(config.get("cookies_file", "cookies.txt"))
    archive_path: Path = Path(config.get("archive_file", "archive.txt"))

    if not cookies_path.is_absolute():
        cookies_path = PROJECT_DIR / cookies_path
    if not archive_path.is_absolute():
        archive_path = PROJECT_DIR / archive_path

    return links, download_path, cookies_path, archive_path


def parse_cookie_file(cookies_file: Path) -> Dict[str, datetime]:
    auth_cookies: Dict[str, datetime] = {}
    with open(cookies_file, "r", encoding="utf-8") as f:
        content = f.read()

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

    return auth_cookies


def check_cookie_expiry(auth_cookies: Dict[str, datetime]) -> Tuple[List[str], List[str]]:
    now = datetime.now()
    expired_cookies: List[str] = []
    expiring_soon: List[str] = []

    for name, expires in auth_cookies.items():
        if name in CRITICAL_COOKIES:
            if now > expires:
                expired_cookies.append(f"{name} ({expires.strftime('%Y-%m-%d')})")
            elif (expires - now).days < 1:
                expiring_soon.append(name)

    return expired_cookies, expiring_soon


def format_cookie_status(auth_cookies: Dict[str, datetime], expired_cookies: List[str], expiring_soon: List[str]) -> Tuple[Optional[bool], str]:
    now = datetime.now()
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


def check_cookie_validity(cookies_file: Path) -> Tuple[Optional[bool], str]:
    if not cookies_file.exists():
        return None, "[WARN] Cookie file not found"

    try:
        auth_cookies = parse_cookie_file(cookies_file)

        if not auth_cookies:
            return None, "[WARN] Cannot parse cookie expiry time"

        expired_cookies, expiring_soon = check_cookie_expiry(auth_cookies)
        return format_cookie_status(auth_cookies, expired_cookies, expiring_soon)

    except Exception as e:
        return None, f"[WARN] Error checking cookie: {e}"


def build_args(link: str, download_path: Path, cookies_file: Path, archive_file: Path) -> List[str]:
    output_template = f"{download_path}/%(uploader)s/%(title)s.%(ext)s"
    args: List[str] = [
        "yt-dlp",
        "-o", output_template,
        "-f", "bestvideo+bestaudio",
        "--merge-output-format", "mp4",
        "--download-archive", str(archive_file),
        "--restrict-filenames",
        "--replace-in-metadata", "uploader", r"[\\/:*?\"<>|]", "_",
        "--replace-in-metadata", "title", r"[\\/:*?\"<>|]", "_",
    ]

    if "space.bilibili.com" not in link:
        args.append("--no-playlist")

    if cookies_file.exists():
        args.extend(["--cookies", str(cookies_file)])

    args.append(link)
    return args


def main() -> None:
    print_header()
    try:
        check_ytdlp()

        links, download_path, cookies_path, archive_path = load_config()

        download_path = check_and_create_directory(download_path)

        if not cookies_path.exists():
            print(f"[WARN] Cookie file not found: {cookies_path}")
            print("[WARN] Will try to download without cookies")
        else:
            is_valid, msg = check_cookie_validity(cookies_path)
            print(msg)
            if is_valid is False:
                raise DownloaderRuntimeError(f"Cookie expired. Please refresh cookies: python scripts/refresh_cookies.py")

        if not links:
            print("[WARN] No links in config.yml")
            return

        print(f"Links count: {len(links)}")
        print(f"Download directory: {download_path}")
        print()

        failed: List[Tuple[str, int]] = []

        for i, link in enumerate(links, 1):
            print("-" * 40)
            print(f"[{i}/{len(links)}] {link}")

            validate_url(link)

            args = build_args(link, download_path, cookies_path, archive_path)
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")

            print()
            for line in process.stdout:
                print(f"  {line.rstrip()}")
            process.wait()

            if process.returncode == 0:
                print("  [OK]")
            else:
                print(f"  [FAIL] exit code: {process.returncode}")
                failed.append((link, process.returncode))

        print()
        print("=" * 40)
        print("  Download Complete")
        if failed:
            print(f"  Failed: {len(failed)} links")
            for link, code in failed:
                print(f"    [{code}] {link}")
        print(f"  Archive: {archive_path}")
        print("=" * 40)

    except DownloaderError as e:
        print(f"[ERROR] {e}")
        sys.exit(e.exit_code)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
