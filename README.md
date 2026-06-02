# B站视频批量下载器

基于 `yt-dlp` 和 `Playwright` 实现的B站视频批量下载工具，支持增量下载和会员视频下载。

## 功能特性

- ✅ **批量下载**: 支持同时下载多个UP主的全部视频
- ✅ **增量下载**: 自动跳过已下载的视频，支持断点续传
- ✅ **会员视频**: 通过Cookie登录获取更高画质
- ✅ **时间过滤**: 支持按日期范围筛选视频
- ✅ **自动合并**: 自动选择最佳音视频质量并合并为MP4

## 文件结构

```
├── scripts/
│   ├── download_bilibili.ps1    # PowerShell下载脚本
│   └── refresh_cookies.py       # Cookie刷新脚本（Playwright）
├── config.yml                    # 配置文件
├── cookies.txt                   # Netscape格式Cookie（需自行获取）
├── archive.txt                   # 增量下载记录
└── .gitignore                    # Git忽略配置
```

## 快速开始

### 1. 安装依赖

```bash
# 安装 yt-dlp
pip install yt-dlp

# 安装 Playwright（用于刷新Cookie）
pip install playwright
playwright install chromium
```

### 2. 获取登录Cookie

运行Cookie刷新脚本，扫码登录B站：

```bash
python scripts/refresh_cookies.py
```

### 3. 配置下载链接

编辑 `config.yml`，添加UP主空间链接：

```yaml
# 添加 UP 主空间链接，每行一个
link:
  - https://space.bilibili.com/12345678
  - https://space.bilibili.com/87654321

# 下载目录
path: C:\Downloads\Bilibili

# 时间过滤（可选）
start_time: "2024-01-01"
end_time: "2024-12-31"
```

### 4. 开始下载

```powershell
.\scripts\download_bilibili.ps1
```

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `link` | UP主空间链接列表 | 空 |
| `path` | 视频下载目录 | 需配置 |
| `start_time` | 开始日期过滤（YYYY-MM-DD） | 空 |
| `end_time` | 结束日期过滤（YYYY-MM-DD） | 空 |
| `cookies_file` | Cookie文件路径 | `cookies.txt` |
| `archive_file` | 增量记录文件 | `archive.txt` |

## 注意事项

- `cookies.txt` 包含敏感信息，已添加到 `.gitignore`
- 首次使用需运行 `refresh_cookies.py` 获取登录Cookie
- 建议定期刷新Cookie以保持登录状态
- 下载视频请遵守B站用户协议

## License

MIT