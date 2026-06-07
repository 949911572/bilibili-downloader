# B站视频批量下载器

> 简单的 yt-dlp 调用脚本，没什么黑科技，就是帮你省去手敲命令。

---

## 使用方法

### 1. 安装依赖

```bash
pip install yt-dlp playwright
playwright install chromium
```

### 2. 获取 Cookie

```bash
python scripts/refresh_cookies.py
```
扫码登录B站后自动保存到 `cookies.txt`。

### 3. 配置

复制 `config.example.yml` 为 `config.yml`，修改以下配置：

```yaml
link:
  - https://www.bilibili.com/video/BV1xxx

path: ./Downloaded    # 下载目录（相对路径）
```

### 4. 运行

```bash
python scripts/download_bilibili.py
```

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `scripts/download_bilibili.py` | 主脚本（Python） |
| `scripts/download_bilibili.ps1` | 主脚本（PowerShell） |
| `scripts/refresh_cookies.py` | 获取 Cookie |
| `config.yml` | 下载配置 |
| `cookies.txt` | 登录凭证 |
| `archive.txt` | 增量记录 |

---

## 注意事项

- Cookie 会过期，下载失败时运行 `refresh_cookies.py` 刷新
- 本质就是 `yt-dlp` 命令的批量封装
- 请遵守B站用户协议
