# JB Video Doctor

A simple, private local web tool that repairs corrupted or unplayable video files and converts them into a widely-compatible **MP4 (H.264/AAC)** that works in Clipchamp, browsers, and video editors. Runs 100% on your PC — no cloud uploads.

## Features
- Upload a corrupted `.wmv` (or other) video file in the browser.
- Repairs errors and discards damaged frames using **ffmpeg**.
- Converts to a broadly compatible **MP4 (H.264 + AAC)**.
- Download the fixed file with one click.

## Requirements
- **Python 3.10+**
- **Flask** — `pip install flask`
- **ffmpeg** on your system (install via `winget install Gyan.FFmpeg`)

## Usage
1. Double-click `Start.bat` (Windows), or run:
   ```bash
   python app.py
   ```
2. Open http://127.0.0.1:5000 in your browser.
3. Choose your video file, click **Repair video**, then download the repaired MP4.

Processed files are stored locally under `File/uploads` (source, auto-deleted) and `File/repaired` (output).

## How it works
Many editors (like Clipchamp) reject `.wmv` files even when the video itself is fine. This tool re-encodes the input to H.264/AAC MP4 — fixing genuine corruption (by discarding damaged packets) and format-compatibility issues at the same time.

## License
MIT
