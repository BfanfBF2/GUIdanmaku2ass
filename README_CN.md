# B站弹幕下载与转换工具（图形界面）

[English](./README.md) | [下载 App](https://github.com/BfanfBF2/GUIdanmaku2ass/archive/refs/heads/main.zip)

一款跨平台的 B 站弹幕批量下载、转换为 ASS 字幕，并自动重命名整理到对应文件夹的图形化工具。基于 Python + Tkinter 开发。

![截图](screenshot.png) 

---
## 新功能
- **1.0.2**：新增合并弹幕功能
---

## 功能特点

- **批量下载**：在文本框中逐行输入多个视频/番剧链接，目前测试支持所有格式，包括BV、AV、EP 或 b23.tv 短链接，网页直接点击分享复制得到的含有网址的不标准格式也可以自动提取。
- **屏蔽 UID**：可过滤特定用户的弹幕（在 `bdanmaku.sh` 中自定义 `BLOCK_UIDS` 数组）。
- **自动重命名与移动**：转换后根据用户定义的规则重命名 `.ass` 文件，并移动到 `~/Movies/<文件夹>`。
- **防风控延迟**：可配置每个链接处理后的等待秒数，避免触发频率限制。
- **设置持久化**：链接和规则分别保存在 `~/danmaku2ass/links.txt` 和 `rules.txt` 中，下次启动自动加载。

---

## 安装

1. **克隆仓库**或下载 ZIP 包：
   ```bash
   git clone https://github.com/yourusername/bilibili-danmaku-tool.git
   cd bilibili-danmaku-tool
   ```

2. **将文件放置到 `~/danmaku2ass`**（即`/Users/<your_username>/danmaku2ass`，程序默认读取该目录）：

   ```bash
   mkdir -p ~/danmaku2ass
   cp bdanmaku.sh renameass.py danmaku2ass.py gui.py ~/danmaku2ass/
   chmod +x ~/danmaku2ass/bdanmaku.sh
   ```

3. **运行 B站弹幕下载.app**

---

## 使用方法

1. **输入 B 站链接**：在顶部文本框内每行一个链接。支持格式：
   - `BV1xx411c7mD`
   - `av123456`
   - `ep123456`（番剧剧集 ID）
   - `https://b23.tv/xxxxx`（短链接）
   - `https://www.bilibili.com/video/BVxxxxx`（标准网址）
   - `【xxxxxxx】 https://www.bilibili.com/video/BVxxxxx`（网页点击分享复制文本）
   
2. **定义重命名规则**（可选）：点击“添加规则”，填写：
   
   - **关键词**：下载的 `.ass` 文件名中含有的文本（例如 `"孤独摇滚"`）。
   - **目标文件夹模板**：最终的文件夹名和文件命名格式，使用 `{ep:02d}` 表示集数（例如 `[Nekomoe kissaten][Bocchi the Rock!][{ep:02d}][1080p][CHS]`）。
   
   程序会在文件名中搜索关键词，匹配后根据模板重命名并移动到 `~/Movies/<文件夹名>`。
   
3. **调整防风控延迟**：在“高级设置”中设置每个链接处理后的等待秒数（0~60 秒）。

4. 点击 **“开始处理”** 启动任务。进度条和日志会实时更新。如需中断，点击 **“停止”**。

5. 转换完成后，所有 `.ass` 文件会按规则放在 `~/Movies/<对应文件夹>` 下，并重命名。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `gui.py` | 主程序（Tkinter 图形界面） |
| `bdanmaku.sh` | Shell 脚本，调用 `danmaku2ass.py` 下载弹幕并转换 |
| `renameass.py` | Python 脚本，根据规则重命名并移动 ASS 文件 |
| `danmaku2ass.py` | 核心转换引擎（来自 [danmaku2ass](https://github.com/m13253/danmaku2ass)） |
| `links.txt` | 用户保存的链接文件 |
| `rules.txt` | 用户保存的重命名规则文件（格式：`关键词\|模板`） |
| `app.ico` | 应用图标（可选） |
| `B站弹幕下载.app.zip` | 预打包的 macOS 应用程序（解压后双击运行） |

---

## 自定义配置

- **屏蔽 UID**：编辑 `bdanmaku.sh` 中的 `BLOCK_UIDS` 数组，添加要屏蔽的用户 ID（十六进制）。

  

  > [!NOTE]
  >
  > ### 用户ID查询方式
  >
  > 1.前往 `https://api.bilibili.com/x/player/pagelist?bvid=<BVxxxxx>` 在末尾输入视频的BV号
  >
  > 2.复制获取的json文件中cid一项，粘贴到 `https://comment.bilibili.com/<cid>.xml` 网址中cid位置
  >
  > 3.找到想要屏蔽的弹幕，前方第7项的十六进制文本即为用户 ID，复制它。
  >
  > 4.在 `BLOCK_UIDS` 中粘贴。

  

- **默认目录**：可修改 `gui.py` 和 `renameass.py` 中的 `DANMAKU_DIR` 和 `TARGET_ROOT`。

- **ASS 转换参数**：调整 `bdanmaku.sh` 中 `danmaku2ass.py` 的参数（如 `-fs`、`-dm`、`-ds`、`-p`），详见 `danmaku2ass.py -h`。

---

## 常见问题

- **权限错误**：确保 `bdanmaku.sh` 有可执行权限（`chmod +x`）。
- **缺少 danmaku2ass.py**：本仓库已包含该文件，请将其放在 `~/danmaku2ass` 目录下。

---

## 许可证

MIT License – 可自由使用和修改。

---

## 致谢

- [danmaku2ass](https://github.com/m13253/danmaku2ass) 作者 m13253 提供的核心转换引擎。
- Bilibili API 提供弹幕数据。

---

**祝使用愉快！** 如有问题，欢迎在 GitHub 提 Issue。
