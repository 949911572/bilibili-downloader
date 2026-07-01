# B站视频批量下载器

> 基于 yt-dlp 的视频下载脚本，支持批量下载、增量下载、Cookie 过期检测等功能。

---

## 使用方法

### 1. 安装依赖

**要求**: Python 3.9+

还需要安装 [ffmpeg](https://ffmpeg.org/)（用于合并音视频）：
- Windows: 从 [ffmpeg 官网](https://ffmpeg.org/download.html) 下载并添加到 PATH，或使用 `winget install Gyan.FFmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 获取 Cookie

```bash
python scripts/refresh_cookies.py
```

扫码登录 B 站后自动保存到 `cookies.txt`。

### 3. 配置

复制 `config.example.yml` 为 `config.yml`：

```yaml
# 视频链接或UP主空间链接，每行一个
link:
  - https://www.bilibili.com/video/BV1xxx
  - https://space.bilibili.com/12345678

# 下载目录（相对路径）
path: ./Downloaded

# Cookie 文件路径（默认 cookies.txt，可不用改）
cookies_file: cookies.txt

# 增量记录文件（默认 archive.txt，可不用改）
archive_file: archive.txt
```

**支持的链接类型：**
- UP主空间: `https://space.bilibili.com/12345678`
- 单视频: `https://www.bilibili.com/video/BV1xxx`
- 多P视频指定分P: `https://www.bilibili.com/video/BV1xxx?p=2`

### 4. 运行

```bash
python scripts/download_bilibili.py
```

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `scripts/download_bilibili.py` | 主脚本（批量下载） |
| `scripts/refresh_cookies.py` | 获取 Cookie |
| `scripts/utils.py` | 公共工具模块 |
| `config.yml` | 下载配置 |
| `config.example.yml` | 配置示例模板 |
| `cookies.txt` | 登录凭证 |
| `archive.txt` | 增量下载记录 |
| `Downloaded/` | 下载目录（按 UP 主分类） |
| `requirements.txt` | Python 依赖 |

---

## 常见问题

### Cookie 过期怎么办？
脚本启动时会自动检测 Cookie 过期状态。如果提示过期，运行：
```bash
python scripts/refresh_cookies.py
```
重新扫码登录即可。

### 下载的视频画质不高？
- 检查 Cookie 是否有效（会员视频需要大会员账号）
- 确保登录的是有权限的账号
- 运行 `python scripts/refresh_cookies.py` 刷新 Cookie

### 某些视频下载失败？
可能原因：
- 视频已删除或设置为私密
- 网络连接问题或 B 站限流
- 链接格式不正确

解决方法：
- 手动在浏览器中打开链接，确认视频可用
- 稍后重试
- 检查网络连接

### Playwright / Chromium 安装失败？
- 确保网络畅通
- 手动安装：`playwright install chromium`
- 或手动从浏览器导出 Cookie 保存为 Netscape 格式

### 视频下载后无法播放？
- 可能是下载未完成（文件损坏），删除后重新下载
- 尝试使用 VLC 等兼容性更好的播放器
- 检查 yt-dlp 输出是否有错误提示

### 安全错误（退出码 3）？
- 检查 `config.yml` 中的 `path` 是否使用了相对路径（如 `./Downloaded`）
- 确保下载路径在项目目录范围内
- 检查链接是否为有效的 B 站链接（仅允许 bilibili.com 和 b23.tv）

### archive.txt 丢失了怎么办？
删除损坏的 archive.txt 后重新运行脚本，文件会自动重建。
注意：重建后已下载的视频会被重新检测，但不会重复下载（yt-dlp 会根据文件名判断）。

---

## 已知限制

- **Cookie 有效期**：B 站 Cookie 会定期过期，需要人工扫码重新获取（无法自动刷新）
- **会员视频画质**：下载画质取决于登录账号的会员等级，平台限制无法绕过
- **下载速度**：受网络带宽和 B 站服务器限速影响，大量视频下载可能较慢
- **视频可用性**：已删除、私密或仅限特定用户观看的视频无法下载

---

## 代码质量

本项目经过严格的代码审查，包含以下安全和质量保障：

### 安全特性
- **命令注入防护**：路径验证、URL 白名单、参数安全校验
- **路径遍历防护**：下载路径限制在项目目录范围内
- **Cookie 安全**：认证 Cookie 过期检测、关键 Cookie 校验
- **文件名安全**：特殊字符过滤、非法字符替换

### 代码质量
- **统一异常处理**：自定义异常体系，不同错误类型对应不同退出码
- **模块化设计**：公共逻辑提取到 `utils.py`
- **类型提示**：完整的 Python 类型注解
- **实时进度输出**：下载进度实时单行刷新显示

---

## 注意事项

- Cookie 会过期，脚本会自动检测过期状态，过期时提示刷新命令
- 本质就是 `yt-dlp` 命令的批量封装
- 请遵守 B 站用户协议

---

## 错误码说明

脚本通过不同的退出码来标识错误类型，便于问题排查：

| 退出码 | 错误类型 | 含义 | 常见场景 |
|--------|---------|------|---------|
| 0 | 成功 | 执行完成，无错误 | 正常下载完成 |
| 1 | 通用错误 | 未预期的异常 | 程序内部错误 |
| 2 | 配置错误 | 配置文件相关问题 | 配置文件缺失、配置项错误 |
| 3 | 安全错误 | 安全校验失败 | 路径遍历攻击、恶意 URL、域名不在白名单 |
| 4 | 运行时错误 | 运行过程中的错误 | 依赖缺失（yt-dlp/ffmpeg）、目录创建失败、写入权限不足、Cookie 过期 |

**排查建议**：
- 退出码 2：检查 `config.yml` 文件是否存在且格式正确
- 退出码 3：检查配置的下载路径和链接是否合法
- 退出码 4：检查 yt-dlp/ffmpeg 是否安装、下载目录权限是否足够、Cookie 是否过期

---

## 免责声明

本项目仅用于技术研究、学习交流与个人数据管理。请在合法合规前提下使用：

- 不得用于侵犯他人隐私、版权或其他合法权益
- 不得用于任何违法违规用途
- 使用者应自行承担因使用本项目产生的全部风险与责任
- 如平台规则、接口策略变更导致功能失效，属于正常技术风险

如果你继续使用本项目，即视为已阅读并同意上述声明。
