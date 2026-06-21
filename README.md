# pi-webcam

Raspberry Pi webcam that captures periodic snapshots of a fixed outdoor scene.
Automatically calibrates camera parameters (exposure, gain, white balance) for the
current light conditions and uploads images to a remote server.

## Hardware

- Raspberry Pi 3 Model B or B+
- Raspberry Pi Camera Module v2 (IMX219) — standard or NoIR variant
- Camera mounted upside down (rotation handled in software)

## Requirements

- Raspberry Pi OS Debian 11 (Bullseye) or later
- `picamera2` installed via apt (included in Raspberry Pi OS by default from Bullseye onwards)
- `uv` for Python environment management

Install `uv` if not already present:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

### On Raspberry Pi

```bash
git clone git@github.com:warsz/pi_webcam2.git
cd pi_webcam2

# --system-site-packages: makes system-installed picamera2 visible inside the venv
# --python python3.13: required because .python-version pins to 3.11 (set on Mac)
#   but picamera2 is installed under system Python 3.13 on Debian 13
uv venv --system-site-packages --python python3.13 .venv
source .venv/bin/activate

uv pip install -e .
```

### On Mac (development only — no camera)

```bash
git clone git@github.com:warsz/pi_webcam2.git
cd pi_webcam2

uv venv .venv
source .venv/bin/activate

uv pip install -e .
```

Note: `picamera2` is not available on Mac. Camera code cannot be run locally —
deploy to the Pi via git and run it there.

## Configuration

Copy or edit `config.toml` to match your setup:
```bash
cp config.toml.example config.toml   # once example file exists
```

Key settings to review:
- `camera.module` — `"standard"` or `"noir"` depending on your camera module
- `image.location_name` — displayed as label on every captured image
- `image.latest_path` / `image.archive_dir` — where images are saved
- `metering.light_region` / `metering.white_reference_region` — pixel regions used
  for light metering and white balance calibration (use the setup page in the web UI
  to find the right coordinates)

Create a `.env` file for upload credentials (never commit this):
```bash
FTP_HOST=your.server.com
FTP_USER=username
FTP_PASS=password
```

## Running

```bash
# Single capture (auto-calibrates if no calibration data exists for current light level)
python snapshot.py

# Force re-calibration before capturing
python snapshot.py --calibrate

# Start the web UI (view latest image + calibration state)
python web/app.py
```

The web UI is available at `http://<pi-ip>:5001` from any browser on the same network.

> **Status**: `snapshot.py` and `web/app.py` are not yet implemented (Phase 3–4). During
> development, use `python camera.py` for a single capture and serve the output folder with
> `python3 -m http.server 8080` to view images in a browser.

## Development notes

- Always edit code on Mac and deploy via git (`git push` → `git pull` on Pi). Editing directly
  on the Pi causes local changes that block the next pull.
- `capture_array()` in picamera2 returns **RGB** format (not BGR). Channel indices in
  `meter_white` and any future array processing must use 0=R, 1=G, 2=B.
- White balance calibration (`run_sweep`) must be run **outdoors in daylight**. Indoor warm
  incandescent light has essentially no blue content (r/b ≈ 479 measured), making it impossible
  to calibrate against.

## Development

See `APPROACH.md` for the development methodology used in this project.
See `plan.md` for the current task list and architecture decisions.
