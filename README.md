# GUIdanmaku2ass
An easy-to-use GUI application for downloading danmaku from Bilibili, converting them to ass subtitle files, renaming them to the desired format, and automatically moving them to the desired folder
下面是两个 README 文件的内容。  
**请将以下内容分别保存为 `README.md`（英文）和 `README_CN.md`（中文），并放在仓库根目录。**

---

### `README.md`（英文）


# Bilibili Danmaku Downloader & Converter (GUI)

[中文版](./README_CN.md) | [Download App](#download)

A cross-platform GUI tool for batch downloading Bilibili danmaku (bullet comments) and converting them to ASS subtitle format, with automatic renaming and moving to organized folders. Built with Python + Tkinter.

![Screenshot](screenshot.png) *(Add your screenshot here)*

---

## Features

- **Batch Download**: Input multiple video/bangumi links (BV, AV, EP, or b23.tv short links) in a text area.
- **Real-time Progress**: Shows current task count, progress bar, and live log output.
- **Stop/Cancel**: Interrupt the process at any time.
- **UID Blocking**: Filter out danmaku from specific users (customizable in `bdanmaku.sh`).
- **Auto Rename & Move**: After conversion, rename `.ass` files according to user-defined rules and move them to `~/Movies/<anime_folder>`.
- **Anti-Spam Delay**: Configurable sleep time between link processing to avoid rate limiting.
- **Persistent Settings**: Links and rules are saved to `links.txt` and `rules.txt` in `~/danmaku2ass`.

---

## Requirements

- macOS (tested on Big Sur+), also works on Linux with minor adjustments.
- Python 3.6+
- Tkinter (usually included with Python, but may need `python3-tk` on Linux)
- `curl` and `bash` (pre-installed on macOS/Linux)

---

## Installation

1. **Clone this repository** or download the ZIP:
   ```bash
   git clone https://github.com/yourusername/bilibili-danmaku-tool.git
   cd bilibili-danmaku-tool
   ```

2. **Place the files** in `~/danmaku2ass` (the app expects this location):
   ```bash
   mkdir -p ~/danmaku2ass
   cp bdanmaku.sh renameass.py danmaku2ass.py gui.py ~/danmaku2ass/
   chmod +x ~/danmaku2ass/bdanmaku.sh
   ```

   *Alternatively, you can keep them anywhere and modify the paths in `gui.py`, but the default is `~/danmaku2ass`.*

3. **Install Python dependencies** (if any) – none required besides standard library.

4. **Run the GUI**:
   ```bash
   python3 ~/danmaku2ass/gui.py
   ```

---

## Usage

1. **Enter Bilibili links** in the top text area (one per line). Supported formats:
   - `BV1xx411c7mD`
   - `av123456`
   - `ep123456` (bangumi episode ID)
   - `https://b23.tv/xxxxx` (short link)

2. **Define renaming rules** (optional). Click “添加规则” and fill in:
   - **Keyword**: text that appears in the downloaded `.ass` filename (e.g., `"成为了朋友"`).
   - **Target folder template**: the final directory name and file pattern, using `{ep:02d}` for episode number (e.g., `[ANi] My Friend - {ep:02d} [1080p]`).

   The tool will search for the keyword in the filename and, if matched, rename and move the file to `~/Movies/<folder_from_template>`.

3. **Adjust anti-spam delay** in the “Advanced Settings” section (0–60 seconds between links).

4. Click **“开始处理”** to start. The progress bar and log will update in real time. You can click **“停止”** to abort.

5. After conversion, all `.ass` files will be placed in `~/Movies/<anime_folder>` with the new names.

---

## File Structure

| File | Description |
|------|-------------|
| `gui.py` | Main GUI application (Tkinter). |
| `bdanmaku.sh` | Shell script that downloads danmaku and converts to ASS using `danmaku2ass.py`. |
| `renameass.py` | Python script that renames and moves ASS files based on rules. |
| `danmaku2ass.py` | Core converter (from [danmaku2ass](https://github.com/m13253/danmaku2ass)). |
| `links.txt` | Example / user-saved links file. |
| `rules.txt` | Example / user-saved renaming rules (format: `keyword\|template`). |
| `app.ico` | Windows icon (optional). |
| `B站弹幕下载.app.zip` | Pre-packaged macOS application (double-click to run). |

---

## Packaging as a macOS App

To create a standalone `.app`:

```bash
pyinstaller --windowed --name "B站弹幕下载" --icon app.icns gui.py
```

*(Note: `app.icns` is required for macOS icon; if you only have `app.ico`, convert it first.)*

The resulting app will be in `dist/`. You can distribute the `.app` or compress it as a ZIP.

---

## Customization

- **Blocked UIDs**: Edit the `BLOCK_UIDS` array in `bdanmaku.sh` to filter specific users.
- **Default directories**: Change `DANMAKU_DIR` and `TARGET_ROOT` in `gui.py` and `renameass.py`.
- **ASS conversion parameters**: Adjust `-fs`, `-dm`, `-ds`, `-p` in `bdanmaku.sh` (see `danmaku2ass.py -h`).

---

## Troubleshooting

- **“No module named tkinter”**: Install Tkinter (`sudo apt-get install python3-tk` on Debian/Ubuntu, or use Homebrew on macOS: `brew install python-tk`).
- **Logs not showing in real time**: The tool uses PTY to force line buffering – if it still lags, ensure `PYTHONUNBUFFERED=1` is set (already in the scripts).
- **Permission denied**: Make sure `bdanmaku.sh` has execute permission (`chmod +x`).
- **Missing danmaku2ass.py**: The file is included in this repository; place it in `~/danmaku2ass`.

---

## License

MIT License – feel free to use and modify.

---

## Acknowledgements

- [danmaku2ass](https://github.com/m13253/danmaku2ass) by m13253 for the core conversion engine.
- Bilibili API for providing danmaku data.

---

**Enjoy!** If you encounter issues, please open an issue on GitHub.
