# B站视频批量下载器

> 一个简单的 **yt-dlp 调用脚本**，没有复杂的封装，只是帮你省去手敲 yt-dlp 命令的麻烦。

基于 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 实现对B站视频的批量下载，配合 Playwright 自动获取 Cookie 以支持高画质/会员视频下载。

---

## 使用方法

### 1. 安装依赖

```bash
pip install yt-dlp playwright
playwright install chromium
```

### 2. 获取 Cookie

运行脚本会自动打开浏览器，扫码登录B站后 Cookie 保存到 `cookies.txt`：

```bash
python scripts/refresh_cookies.py
```

### 3. 配置下载列表

复制 `config.example.yml` 为 `config.yml`，填入要下载的链接：

```yaml
link:
  - https://space.bilibili.com/12345678          # UP主空间（下载全部视频）
  - https://www.bilibili.com/video/BV1k957zgE1e   # 单个视频
  - https://www.bilibili.com/video/BV1k957zgE1e?p=2  # 多P视频的某一P

path: C:\Downloads\Bilibili    # 下载目录

start_time: "2024-01-01"       # 可选：只下载该日期之后的视频
end_time: "2024-12-31"         # 可选：只下载该日期之前的视频
```

### 4. 开始下载

```powershell
.\scripts\download_bilibili.ps1
```

脚本会遍历配置中的每个链接，调用 yt-dlp 下载，已下载的视频（记录在 `archive.txt`）会自动跳过。

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `scripts/download_bilibili.ps1` | 主脚本：读取配置、调用 yt-dlp 下载 |
| `scripts/refresh_cookies.py` | 用 Playwright 打开浏览器，扫码获取 Cookie |
| `config.yml` | 下载配置（链接、路径、时间过滤） |
| `cookies.txt` | 登录凭证（Netscape 格式，已加入 .gitignore） |
| `archive.txt` | 增量记录，避免重复下载 |

---

## 注意事项

- `cookies.txt` 包含登录凭证，**切勿上传到公开仓库**
- Cookie 会过期，偶尔重新运行 `refresh_cookies.py` 刷新即可
- 本质上就是 `yt-dlp -o ... -f bestvideo+bestaudio --cookies cookies.txt <链接>` 的批量封装，不是什么黑科技
- 请遵守B站用户协议，仅下载有权获取的视频

---

## License

MIT
