# B站视频批量下载器

> 简单的 yt-dlp 调用脚本，没什么黑科技，就是帮你省去手敲命令。

---

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
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
| `scripts/refresh_cookies.py` | 获取 Cookie |
| `config.yml` | 下载配置 |
| `cookies.txt` | 登录凭证 |
| `archive.txt` | 增量记录 |
| `Downloaded/` | 下载目录 |
| `link-backup/` | 已完成链接备份目录 |

---

## 注意事项

- Cookie 会过期，脚本会自动检测过期状态，过期时提示刷新命令
- 本质就是 `yt-dlp` 命令的批量封装
- 请遵守B站用户协议

---

## 免责声明

本项目仅用于技术研究、学习交流与个人数据管理。请在合法合规前提下使用：

- 不得用于侵犯他人隐私、版权或其他合法权益
- 不得用于任何违法违规用途
- 使用者应自行承担因使用本项目产生的全部风险与责任
- 如平台规则、接口策略变更导致功能失效，属于正常技术风险

如果你继续使用本项目，即视为已阅读并同意上述声明。
