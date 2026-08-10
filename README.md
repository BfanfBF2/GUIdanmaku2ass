# Bilibili Danmaku Downloader & Converter (GUI)

[中文版](./README_CN.md) | [Download App](#download)

A cross-platform GUI tool for batch downloading Bilibili danmaku (bullet comments), converting them to ASS subtitle format, and automatically renaming/moving them to organized folders. Built with Python + Tkinter.

![Screenshot](screenshot.png) *(Please add your screenshot here)*

---

## Features

- **Batch Download**: Enter multiple video/bangumi links line by line. Tested to support all common formats including BV, AV, EP, b23.tv short links, and even non‑standard formats copied directly from browser share links (the tool auto‑extracts the ID).
- **UID Blocking**: Filter danmaku from specific users (customize the `BLOCK_UIDS` array in `bdanmaku.sh`).
- **Auto Rename & Move**: After conversion, rename `.ass` files according to user‑defined rules and move them to `~/Movies/<folder>`.
- **Anti‑Spam Delay**: Configurable sleep time between processing each link to avoid rate limiting.
- **Persistent Settings**: Links and rules are saved to `~/danmaku2ass/links.txt` and `rules.txt` respectively, automatically loaded on next launch.

---

## Installation

1. **Clone the repository** or download the ZIP:
   ```bash
   git clone https://github.com/yourusername/bilibili-danmaku-tool.git
   cd bilibili-danmaku-tool
   ```

2. **Place the files** into `~/danmaku2ass` (i.e. `/Users/<your_username>/danmaku2ass`), the default directory the program reads from:
   ```bash
   mkdir -p ~/danmaku2ass
   cp bdanmaku.sh renameass.py danmaku2ass.py gui.py ~/danmaku2ass/
   chmod +x ~/danmaku2ass/bdanmaku.sh
   ```

3. **Run `B站弹幕下载.app`**

---

## Usage

1. **Enter Bilibili links** in the top text area, one per line. Supported formats include:
   - `BV1xx411c7mD`
   - `av123456`
   - `ep123456` (bangumi episode ID)
   - `https://b23.tv/xxxxx` (short link)
   - `https://www.bilibili.com/video/BVxxxxx` (standard URL)
   - `【xxxxxxx】 https://www.bilibili.com/video/BVxxxxx` (text copied from web share)

2. **Define renaming rules** (optional): Click “Add Rule” and fill in:
   - **Keyword**: text that appears in the downloaded `.ass` filename (e.g., `"Bocchi the Rock!"`).
   - **Target folder template**: the final folder name and file pattern, using `{ep:02d}` for episode number (e.g., `[Nekomoe kissaten][Bocchi the Rock!][{ep:02d}][1080p][CHS]`).

   The tool will search for the keyword in the filename and, if matched, rename and move the file to `~/Movies/<folder_from_template>`.

3. **Adjust anti‑spam delay** in the “Advanced Settings” section (0–60 seconds between links).

4. Click **“Start Processing”** to begin. The progress bar and log update in real time. You can click **“Stop”** to abort at any time.

5. After conversion, all `.ass` files are placed in `~/Movies/<corresponding_folder>` with the new names.

---

## File Structure

| File | Description |
|------|-------------|
| `gui.py` | Main GUI application (Tkinter). |
| `bdanmaku.sh` | Shell script that downloads danmaku and converts to ASS using `danmaku2ass.py`. |
| `renameass.py` | Python script that renames and moves ASS files based on rules. |
| `danmaku2ass.py` | Core converter (from [danmaku2ass](https://github.com/m13253/danmaku2ass)). |
| `links.txt` | User‑saved links file. |
| `rules.txt` | User‑saved renaming rules (format: `keyword\|template`). |
| `app.ico` | Application icon (optional). |
| `B站弹幕下载.app.zip` | Pre‑packaged macOS application (unzip and double‑click to run). |

---

## Customization

- **Block UIDs**: Edit the `BLOCK_UIDS` array in `bdanmaku.sh` and add the hexadecimal user IDs you want to block.

  > [!NOTE]
  > ### How to find a user ID
  > 1. Go to `https://api.bilibili.com/x/player/pagelist?bvid=<BVxxxxx>` (replace `<BVxxxxx>` with the video's BV ID).
  > 2. Copy the `cid` value from the returned JSON, then visit `https://comment.bilibili.com/<cid>.xml`.
  > 3. Find the danmaku you want to block; the 7th field (hexadecimal) in the `<d p="...">` tag is the user ID. Copy it.
  > 4. Paste it into the `BLOCK_UIDS` array.

- **Default directories**: Modify `DANMAKU_DIR` and `TARGET_ROOT` in `gui.py` and `renameass.py`.
- **ASS conversion parameters**: Adjust options (e.g., `-fs`, `-dm`, `-ds`, `-p`) for `danmaku2ass.py` inside `bdanmaku.sh`. See `danmaku2ass.py -h` for details.

---

## Troubleshooting

- **Permission errors**: Ensure `bdanmaku.sh` has execute permission (`chmod +x`).
- **Missing danmaku2ass.py**: This repository includes the file; make sure it is placed in `~/danmaku2ass`.

---

## License

MIT License – free to use and modify.

---

## Acknowledgements

- [danmaku2ass](https://github.com/m13253/danmaku2ass) by m13253 for the core conversion engine.
- Bilibili API for providing danmaku data.

---

**Enjoy!** If you encounter any issues, please open an issue on GitHub.
