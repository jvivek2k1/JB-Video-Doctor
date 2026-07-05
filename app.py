"""
WMV Video File Corrector
------------------------
A tiny local web tool to repair corrupted .wmv video files using ffmpeg.

How it works:
  1. You upload a corrupted .wmv file in the browser.
  2. ffmpeg tries to repair it (first a fast lossless remux, then a
     full re-encode that drops corrupted frames if the remux fails).
  3. You download the repaired file.

Everything runs locally on your machine. Files are stored under:
  C:\\AI\\Video_File_Corrector\\File
"""

import os
import shutil
import subprocess
import uuid
from pathlib import Path

from flask import (
    Flask,
    render_template_string,
    request,
    send_from_directory,
    redirect,
    url_for,
    flash,
)
from werkzeug.utils import secure_filename

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
BASE_DIR = Path(r"C:\AI\Video_File_Corrector\File")
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "repaired"

for d in (UPLOAD_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Allow files a bit larger than 200 MB just in case.
MAX_UPLOAD_BYTES = 1024 * 1024 * 1024  # 1 GB

# Prefer the ffmpeg installed by winget; fall back to whatever is on PATH.
_WINGET_FFMPEG = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Microsoft"
    / "WinGet"
    / "Packages"
    / "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    / "ffmpeg-8.1.2-full_build"
    / "bin"
    / "ffmpeg.exe"
)
FFMPEG = str(_WINGET_FFMPEG) if _WINGET_FFMPEG.exists() else (shutil.which("ffmpeg") or "ffmpeg")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
app.secret_key = "video-file-corrector-local"


# --------------------------------------------------------------------------- #
# Repair logic
# --------------------------------------------------------------------------- #
def _run_ffmpeg(args):
    """Run ffmpeg and return (success, log_tail)."""
    proc = subprocess.run(
        [FFMPEG, "-hide_banner", "-y", *args],
        capture_output=True,
        text=True,
    )
    log_tail = "\n".join(proc.stderr.strip().splitlines()[-15:])
    return proc.returncode == 0, log_tail


def repair_video(input_path: Path, output_path: Path):
    """
    Repair a corrupted video AND convert it to a widely-compatible MP4
    (H.264 video + AAC audio).

    Converting to MP4 fixes two problems at once:
      * actual corruption (damaged/incomplete packets are discarded), and
      * format-compatibility (many editors such as Clipchamp reject .wmv
        files even when the video itself is perfectly fine).

    Returns (success: bool, method: str, log: str).
    """
    # Attempt 1: re-encode to H.264/AAC MP4 while ignoring/discarding any
    # corrupted packets. This is the universal fix that produces a file
    # that plays and imports almost everywhere.
    ok, log = _run_ffmpeg(
        [
            "-err_detect", "ignore_err",
            "-fflags", "+discardcorrupt+genpts",
            "-i", str(input_path),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(output_path),
        ]
    )
    if ok and output_path.exists() and output_path.stat().st_size > 1024:
        return True, "Converted to MP4 (H.264/AAC)", log

    # Attempt 2: same conversion but also drop the audio track, in case a
    # damaged audio stream is what's blocking the conversion.
    ok, log = _run_ffmpeg(
        [
            "-err_detect", "ignore_err",
            "-fflags", "+discardcorrupt+genpts",
            "-i", str(input_path),
            "-an",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(output_path),
        ]
    )
    if ok and output_path.exists() and output_path.stat().st_size > 1024:
        return True, "Converted to MP4, video only (audio was unrecoverable)", log

    return False, "Failed", log


# --------------------------------------------------------------------------- #
# Web UI
# --------------------------------------------------------------------------- #
PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WMV Video File Corrector</title>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: "Segoe UI", system-ui, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .card {
      background: #1e293b;
      padding: 40px;
      border-radius: 16px;
      width: min(560px, 92vw);
      box-shadow: 0 20px 50px rgba(0,0,0,.4);
    }
    h1 { margin: 0 0 6px; font-size: 24px; }
    p.sub { margin: 0 0 26px; color: #94a3b8; font-size: 14px; }
    .drop {
      border: 2px dashed #475569;
      border-radius: 12px;
      padding: 32px;
      text-align: center;
      cursor: pointer;
      transition: .2s;
    }
    .drop:hover { border-color: #38bdf8; background: #172033; }
    input[type=file] { display: none; }
    .fname { margin-top: 14px; color: #38bdf8; font-size: 14px; word-break: break-all; }
    button {
      margin-top: 22px;
      width: 100%;
      padding: 14px;
      font-size: 16px;
      font-weight: 600;
      border: 0;
      border-radius: 10px;
      background: #38bdf8;
      color: #0f172a;
      cursor: pointer;
    }
    button:disabled { opacity: .5; cursor: not-allowed; }
    .flash { padding: 12px 14px; border-radius: 10px; margin-bottom: 18px; font-size: 14px; }
    .flash.err { background: #7f1d1d; color: #fecaca; }
    .flash.ok  { background: #14532d; color: #bbf7d0; }
    a.download {
      display: block; text-align: center; margin-top: 14px;
      padding: 14px; border-radius: 10px; background: #22c55e;
      color: #052e16; font-weight: 600; text-decoration: none;
    }
    .method { font-size: 13px; color: #94a3b8; margin-top: 10px; text-align:center; }
    .spinner { display:none; margin-top:18px; text-align:center; color:#94a3b8; font-size:14px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>WMV Video File Corrector</h1>
    <p class="sub">Upload a corrupted .wmv file. It is repaired and converted to a widely-compatible MP4 (works in Clipchamp, browsers, etc.). Runs 100% locally.</p>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for cat, msg in messages %}
        <div class="flash {{ cat }}">{{ msg }}</div>
      {% endfor %}
    {% endwith %}

    {% if download_name %}
      <a class="download" href="{{ url_for('download', filename=download_name) }}">⬇ Download repaired MP4</a>
      <div class="method">Method used: {{ method }}</div>
    {% endif %}

    <form method="post" enctype="multipart/form-data" action="{{ url_for('repair') }}"
          onsubmit="document.getElementById('go').disabled=true; document.getElementById('spin').style.display='block';">
      <label class="drop" for="file">
        <div>📁 Click to choose a .wmv file (or drop it here)</div>
        <div class="fname" id="fname"></div>
        <input type="file" name="file" id="file" accept=".wmv" required>
      </label>
      <div class="spinner" id="spin">⏳ Repairing… this can take a few minutes for large files.</div>
      <button type="submit" id="go">Repair video</button>
    </form>
  </div>

  <script>
    const input = document.getElementById('file');
    const fname = document.getElementById('fname');
    const drop  = document.querySelector('.drop');
    input.addEventListener('change', () => {
      fname.textContent = input.files.length ? input.files[0].name : '';
    });
    ['dragover','dragenter'].forEach(e => drop.addEventListener(e, ev => {
      ev.preventDefault(); drop.style.borderColor = '#38bdf8';
    }));
    ['dragleave','drop'].forEach(e => drop.addEventListener(e, ev => {
      ev.preventDefault(); drop.style.borderColor = '#475569';
    }));
    drop.addEventListener('drop', ev => { input.files = ev.dataTransfer.files;
      fname.textContent = input.files.length ? input.files[0].name : ''; });
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(
        PAGE,
        download_name=request.args.get("download"),
        method=request.args.get("method"),
    )


@app.route("/repair", methods=["POST"])
def repair():
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Please choose a .wmv file first.", "err")
        return redirect(url_for("index"))

    if not file.filename.lower().endswith(".wmv"):
        flash("Only .wmv files are supported.", "err")
        return redirect(url_for("index"))

    token = uuid.uuid4().hex[:8]
    safe_name = secure_filename(file.filename)
    input_path = UPLOAD_DIR / f"{token}_{safe_name}"
    file.save(input_path)

    # Output is always an MP4 (H.264/AAC) for maximum compatibility.
    stem = Path(safe_name).stem or "video"
    output_name = f"repaired_{token}_{stem}.mp4"
    output_path = OUTPUT_DIR / output_name

    try:
        ok, method, _log = repair_video(input_path, output_path)
    finally:
        # Clean up the uploaded (corrupted) source file.
        try:
            input_path.unlink(missing_ok=True)
        except OSError:
            pass

    if not ok:
        flash(
            "Sorry, the file could not be repaired. It may be too badly "
            "damaged or not a real video file.",
            "err",
        )
        return redirect(url_for("index"))

    flash("✅ Repair complete! Your download is ready below.", "ok")
    return redirect(url_for("index", download=output_name, method=method))


@app.route("/download/<path:filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    print("=" * 60)
    print("  WMV Video File Corrector")
    print("  Open this in your browser:  http://127.0.0.1:5000")
    print(f"  Using ffmpeg: {FFMPEG}")
    print(f"  Files stored in: {BASE_DIR}")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False)
