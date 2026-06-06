# B站视频批量下载器

基于 `yt-dlp` 和 `Playwright` 实现的B站视频批量下载工具，支持增量下载、会员视频下载和时间范围过滤。

---

## 📌 功能特性

| 功能 | 说明 |
|------|------|
| **批量下载** | 支持同时下载多个UP主空间、合集或单个视频 |
| **增量下载** | 自动跳过已下载的视频，支持断点续传 |
| **会员视频** | 通过Cookie登录获取更高画质视频 |
| **时间过滤** | 支持按日期范围筛选视频 |
| **自动合并** | 自动选择最佳音视频质量并合并为MP4格式 |
| **多P视频** | 正确处理同BV号多P视频（`?p=2` 参数） |

---

## 📁 文件结构

```
bilibili-downloader/
├── scripts/
│   ├── download_bilibili.ps1    # PowerShell下载脚本（主程序）
│   └── refresh_cookies.py       # Cookie刷新脚本（Playwright自动获取）
├── config.yml                    # 下载配置文件（链接、路径、时间过滤）
├── config.example.yml            # 配置示例（不含敏感信息）
├── cookies.txt                   # Netscape格式Cookie（需自行获取）
├── archive.txt                   # 增量下载记录（记录已下载的BV号）
└── .gitignore                    # Git忽略配置（保护敏感文件）
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 yt-dlp（核心下载工具）
pip install yt-dlp

# 安装 Playwright（用于自动获取Cookie）
pip install playwright
playwright install chromium
```

### 2. 获取登录Cookie

运行Cookie刷新脚本，会自动打开浏览器，扫码登录B站即可：

```bash
python scripts/refresh_cookies.py
```

登录成功后，Cookie会自动保存到 `cookies.txt` 文件。

### 3. 配置下载链接

编辑 `config.yml`，添加要下载的视频链接：

```yaml
# 添加视频链接，支持：
# - UP主空间链接: https://space.bilibili.com/12345678
# - 合集链接: https://www.bilibili.com/cheese/xxxx
# - 单视频链接: https://www.bilibili.com/video/BV1xxx
link:
  - https://space.bilibili.com/12345678
  - https://www.bilibili.com/video/BV1k957zgE1e
  - https://www.bilibili.com/video/BV1k957zgE1e?p=2

# 下载目录（Windows路径示例）
path: C:\Users\YourName\Downloads\Bilibili

# 时间过滤：只下载该日期范围内的视频（可选）
start_time: "2024-01-01"
end_time: "2024-12-31"
```

### 4. 开始下载

```powershell
.\scripts\download_bilibili.ps1
```

---

## ⚙️ 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `link` | 视频链接列表（支持UP主空间、合集、单视频） | 空 |
| `path` | 视频下载目录（建议使用绝对路径） | 需配置 |
| `start_time` | 开始日期过滤（格式：YYYY-MM-DD） | 空（不限制） |
| `end_time` | 结束日期过滤（格式：YYYY-MM-DD） | 空（不限制） |
| `cookies_file` | Cookie文件路径 | `cookies.txt` |
| `archive_file` | 增量记录文件路径 | `archive.txt` |

---

## 💡 使用技巧

### 处理多P视频

B站有两种多视频形式：

| 类型 | URL特征 | 说明 |
|------|---------|------|
| **多P视频** | `BV1xxx?p=2` | 同一BV号下的不同分P，共用同一视频页 |
| **合集视频** | `cheese/xxxx` | 多个独立BV号的集合 |

脚本会自动识别并正确处理这两种情况。

### 避免重复下载

- 脚本使用 `archive.txt` 记录已下载的视频ID
- 再次运行时会自动跳过已记录的视频
- 如果需要重新下载，删除 `archive.txt` 即可

---

## ⚠️ 注意事项

1. **Cookie安全**：`cookies.txt` 包含您的B站登录凭证，已添加到 `.gitignore`，请勿上传到GitHub
2. **Cookie有效期**：建议定期运行 `refresh_cookies.py` 刷新Cookie
3. **版权合规**：请遵守B站用户协议，仅下载您有权获取的视频
4. **网络环境**：部分地区可能需要特殊网络环境才能访问B站

---

## 📝 更新日志

### v1.0.0
- 初始版本
- 支持批量下载UP主空间视频
- 支持增量下载
- 支持时间范围过滤
- 支持Cookie登录

---

## 📄 License

MIT License