"""公共工具模块"""
from pathlib import Path


def get_project_root() -> Path:
    """获取项目根目录路径"""
    return Path(__file__).resolve().parent.parent


CRITICAL_COOKIES: set[str] = {"SESSDATA", "bili_jct", "DedeUserID"}

PROJECT_DIR: Path = get_project_root()
CONFIG_FILE: Path = PROJECT_DIR / "config.yml"
COOKIES_PATH: Path = PROJECT_DIR / "cookies.txt"
ARCHIVE_PATH: Path = PROJECT_DIR / "archive.txt"