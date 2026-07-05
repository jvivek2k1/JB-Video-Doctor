# JB Video Doctor 🎬🩺 — Free Video Repair Tool (WMV, MP4, AVI, MKV, MOV)

> **Repair corrupted, broken, or unplayable video files and convert them to a working MP4 — for free, 100% offline on your own PC.**

A simple, private desktop tool that **repairs corrupted or unplayable video files** and converts them into a widely-compatible **MP4 (H.264/AAC)** that works in Clipchamp, web browsers, and video editors. Everything runs **100% on your own PC** — your videos are never uploaded to the cloud.

**Keywords:** video repair, repair corrupted video, fix broken video file, WMV repair, MP4 repair, fix unplayable video, video file corrector, video fixer, convert WMV to MP4, ffmpeg video repair, Clipchamp unsupported file fix, free video repair tool, offline video repair.

---

## 1) What is this app?

Many video files (especially `.wmv`) can become corrupted, unplayable, or get rejected by editors like **Clipchamp** with errors such as *"Unable to import media / unsupported file format"* — even when most of the video is fine.

**JB Video Doctor** fixes this by:
- Repairing errors and discarding any damaged frames using **ffmpeg**.
- Converting the file into a clean, broadly-compatible **MP4 (H.264 video + AAC audio)**.
- Giving you a simple web page in your browser to upload the broken file and download the fixed one.

No accounts, no cloud, no data leaves your machine.

---

## 2) How to clone it to a machine

### Prerequisites (install these first)
| Tool | How to install (Windows) |
|------|--------------------------|
| **Git** | https://git-scm.com/download/win |
| **Python 3.10+** | https://www.python.org/downloads/ (check "Add Python to PATH") |
| **ffmpeg** | Run in a terminal: `winget install Gyan.FFmpeg` |
| **Flask** | Run in a terminal: `pip install flask` |

### Clone the repository
Open **PowerShell** (or Command Prompt) and run:

```bash
git clone https://github.com/jvivek2k1/JB-Video-Doctor.git
cd JB-Video-Doctor
```

---

## 3) How to execute it and open the app

You have two easy options:

**Option A — One click (Windows):**
- Double-click **`Start.bat`**. It launches the app and opens your browser automatically.

**Option B — From a terminal:**
```bash
python app.py
```

Then open this address in your web browser:

👉 **http://127.0.0.1:5000**

You should see the **JB Video Doctor** page.

> To stop the app later, press **Ctrl + C** in the terminal window (or just close the `Start.bat` window).

---

## 4) How to repair a video file — step by step

1. **Start the app** (see section 3) and open **http://127.0.0.1:5000** in your browser.
2. **Select your video:** click the upload box (or drag & drop your corrupted `.wmv` file onto it).
3. **Click "Repair video".**
4. **Wait** while it processes — a "Repairing…" message appears. Large files can take a few minutes.
5. When it finishes, a green **"⬇ Download repaired MP4"** button appears. **Click it** to save the fixed file.
6. **Use the file:** the downloaded `.mp4` now plays and imports correctly (e.g., upload it to Clipchamp — it will be accepted).

**Where files are stored on your PC:**
- Uploaded (broken) files → `File/uploads/` *(automatically deleted after repair)*
- Repaired output files → `File/repaired/`

---

## How it works (technical note)

Editors like Clipchamp often reject `.wmv` files even when the video itself is intact. JB Video Doctor re-encodes the input to **H.264/AAC MP4**, which simultaneously:
- fixes genuine corruption by discarding damaged/incomplete packets, and
- resolves format-compatibility problems.

## Troubleshooting
- **"ffmpeg not recognized"** → install it with `winget install Gyan.FFmpeg` and restart your terminal.
- **"ModuleNotFoundError: flask"** → run `pip install flask`.
- **Page won't open** → make sure `python app.py` is still running, then reload http://127.0.0.1:5000.

## License

Released under the **MIT License with an attribution requirement** — see [LICENSE](LICENSE).

You are free to use, modify, and share this software for any purpose (including commercial), **as long as clear credit is given to the original author, [jvivek2k1](https://github.com/jvivek2k1).**
