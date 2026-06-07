"""
yt-dlp - Bilibili Batch Downloader (Python)
读取 config.yml 中的链接，批量调用 yt-dlp 下载 B 站视频。
"""
import subprocess
import sys
import shutil
from pathlib import Path

import yaml


PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_DIR / "config.yml"
COOKIES_FILE = PROJECT_DIR / "cookies.txt"
ARCHIVE_FILE = PROJECT_DIR / "archive.txt"
DEFAULT_PATH = r"C:\Users\sb\Desktop\0-C\Bilibili\Downloaded"


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
    download_path = config.get("path", DEFAULT_PATH) if config else DEFAULT_PATH

    return links, download_path


def build_args(link, download_path):
    output_template = f"{download_path}/%(uploader)s/%(title)s.%(ext)s"
    args = [
        "yt-dlp",
        "-o", output_template,
        "-f", "bestvideo+bestaudio",
        "--merge-output-format", "mp4",
        "--download-archive", str(ARCHIVE_FILE),
    ]

    if "space.bilibili.com" not in link:
        args.append("--no-playlist")

    if COOKIES_FILE.exists():
        args.extend(["--cookies", str(COOKIES_FILE)])

    args.append(link)
    return args


def main():
    print_header()
    check_ytdlp()

    links, download_path = load_config()

    # 检查下载目录，返回绝对路径
    download_path = check_and_create_directory(download_path)

    if not COOKIES_FILE.exists():
        print(f"[WARN] Cookie file not found: {COOKIES_FILE}")
        print("[WARN] Will try to download without cookies")

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

        args = build_args(link, download_path)
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
    print(f"  Archive: {ARCHIVE_FILE}")
    print("=" * 40)


if __name__ == "__main__":
    main()
