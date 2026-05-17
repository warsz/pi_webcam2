# pi-webcam rewrite plan

## Context

Raspberry Pi webcam installed at a mountain cabin (~1000m altitude) capturing periodic snapshots
of the surrounding landscape. The original code (see `webcam_snapshot.py` and siblings) was a
working but rough implementation using the deprecated `picamera` library. This is a clean rewrite
targeting `picamera2` and modern Python 3.

The old code is kept as reference only. No code from it is carried forward directly.

---

## Hardware

| Device | Model | OS | Role |
|---|---|---|---|
| Local Pi | Raspberry Pi 3 Model B | Debian 13 (Trixie) | Development & test |
| Cabin Pi | Raspberry Pi 3 Model B+ | Debian 10 (Buster) | Production (currently running old code) |

**Camera module**: IMX219 (Camera Module v2, 8MP)
- Rotation: 180° (mounted upside down) — handled in picamera2 config, not post-processing
- Local Pi: likely standard module (IR-cut filter intact)
- Cabin Pi: likely NoIR module (IR-cut filter removed, for night capture)
- `module` type is declared in `config.toml` so the same code runs on both

---

## Architecture decisions

### Camera modules
- `"standard"`: AWB attempted, ColourGains calibrated if needed
- `"noir"`: AWB always disabled, ColourGains always calibrated (AWB is unreliable without IR-cut filter)

### Light level bucketing
- Sample a **sky/open-area region** (`metering.light_region`) → compute mean brightness
- Map to bucket index via `floor(log2(mean_brightness + 1))`
- 12 buckets covers full dynamic range (dark night → bright snow)
- Calibration results stored per bucket in `calibration.toml`

### White balance calibration
- Sample a **known neutral/white surface** visible in the frame (`metering.white_reference_region`)
- Target condition: R mean ≈ G mean ≈ B mean on that surface
- ColourGains swept during calibration; best gains = most neutral white reference

### Quality metric for exposure calibration
- Pixel variance across the full image
- Higher variance = more detail and contrast = better exposed image
- ISO + shutter speed swept during calibration; best combo = highest variance

### Calibration trigger
- Runs automatically when no calibration entry exists for the current light bucket
- Can be forced with `--calibrate` flag
- Results written to `calibration.toml` (machine-generated, not committed to git)

### Image output
- `latest.jpg` — always overwritten, served by the FastHTML web UI
- Timestamped archive image → saved to `archive_dir` → uploaded to remote server
- FTP vs SFTP: **TBD** (see open questions)

### Post-processing
- Pillow (pure Python) replaces ImageMagick `os.system()` calls
- Operations: flip (180°), crop, timestamp annotation, save as JPG

---

## File structure

```
pi-webcam/
├── config.toml           # human-written, committed to git (no secrets)
├── calibration.toml      # machine-written, NOT committed to git
├── .env                  # secrets (FTP credentials), NOT committed to git
├── find_region.py        # helper: capture a frame and identify pixel regions interactively
├── snapshot.py           # main entry point — orchestrates the full capture flow
├── camera.py             # picamera2 wrapper: capture, metering sample, calibration capture
├── calibrate.py          # calibration sweep: vary params, score by variance/channel balance
├── image.py              # Pillow post-processing: crop, annotate, save
├── upload.py             # FTP/SFTP upload logic
├── web/
│   └── app.py            # FastHTML web UI: shows latest.jpg + calibration state
├── requirements.txt
└── plan.md               # this file
```

---

## config.toml structure (agreed)

```toml
[camera]
module = "standard"   # "standard" or "noir"
rotation = 180
resolution = [1920, 1080]

[metering]
# Patch of sky or open area — used to determine light level bucket
light_region = [960, 200, 980, 220]
# Known neutral/white surface visible in frame (e.g. a white sign)
# Used to score white balance quality (target: R ≈ G ≈ B)
white_reference_region = [0, 0, 10, 10]   # TODO: fill in after running find_region.py

[image]
crop = [720, 0, 1200, 1080]       # x_offset, y_offset, width, height
location_name = "Olnessaeter"
latest_path = "/home/pi/pictures/webcam/latest.jpg"
archive_dir = "/home/pi/pictures/webcam/archive"

[server]
# Credentials via env vars: FTP_HOST, FTP_USER, FTP_PASS
remote_dir = "/webcam/"
protocol = "ftp"   # "ftp" or "sftp" — TBD

[calibration]
bucket_count = 12
sweep_iso = [100, 200, 400, 800, 1600]
sweep_shutter_us = [500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, 2000000, 6000000]
sweep_colour_gains = [[1.0, 1.0], [1.5, 1.0], [1.0, 1.5], [2.0, 1.0], [1.0, 2.0]]
```

---

## Working approach

See `APPROACH.md` for the full methodology. The short version:
- One small step at a time, verified on real hardware before moving on
- The human drives, the AI assists
- Code is a thinking tool — write the minimum that makes the next thing visible

## Development workflow

Code is written on Mac, deployed to the local Pi via git (clone + pull). The Pi runs the code
and serves the web UI. Images are viewed via browser at `pi-ip:port` during development.

During early phases (before FastHTML exists), images can be viewed immediately via:
```bash
python3 -m http.server 8080   # run in the image output folder on the Pi
```

### Terminal setup (Ghostty)

Three-pane layout works well for this project:
- Left pane: Mac (editing code)
- Right-top pane: Pi (running code, viewing output)
- Right-bottom pane: Pi (quick edits, git operations)

Split the right pane with `Cmd+Shift+-` (horizontal split).

### Git workflow on Pi

All edits should be made on Mac and deployed via git pull on the Pi. Editing directly
on the Pi causes local changes that block the next pull. If you edited on the Pi and
don't need those changes:

```bash
git checkout -- .   # discard local changes
git pull            # then pull cleanly
```

**TODO**: tighten the deploy loop so testing on Pi is faster and there's less temptation
to edit directly there. Options to explore: `rsync` watch script, SSH remote run from Mac,
or a Makefile with a `deploy` target.

### Virtual environment

Use `uv` for environment and package management. On the Pi, `picamera2` is a system package
(installed via apt, depends on `libcamera`) and cannot be pip-installed. Use
`--system-site-packages` so the venv can see it:

```bash
# On the Pi
# --python python3.13 required: .python-version pins to 3.11 (set on Mac) but picamera2
# is installed under system Python 3.13 on Debian 13. Version must match.
uv venv --system-site-packages --python python3.13 .venv
source .venv/bin/activate
uv pip install -e .   # reads pyproject.toml — do not use -r requirements.txt

# On Mac (no picamera2)
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

## Task list

### Phase 1 — Repo & camera layer

- [x] **T01** New git repo — created `pi_webcam2`, pushed to GitHub, cloned to Pi
  - `pyproject.toml` replaces `requirements.txt` as dependency source
  - `.gitignore` covers `calibration.toml`, `.env`, `__pycache__`, image output dirs
  - `uv` used for environment management

- [x] **T02** `camera.py` — picamera2 wrapper
  - [x] Configure rotation, resolution from config.toml
  - [x] Capture to file (latest_path from config)
  - [x] `meter_light(arr, light_region) -> float` — pure function, takes numpy array
  - [x] `meter_white(arr, white_region) -> tuple[float, float]` — returns (r/g, r/b) ratios
  - [x] `capture(cam, params) -> PIL.Image` — sets runtime controls, returns PIL Image
  - Note: `white_region` still uses placeholder coords [0,0,10,10] — finalize in T09 setup page
  - Note: config key renamed from `white_reference_region` to `white_region`

- [x] **T03** `config.toml` — completed
  - rotation, resolution, paths, metering regions, calibration sweep params
  - `rotation` is per-device (local Pi = `"hflip"`, cabin Pi TBD)
  - `module = "noir"` confirmed for local Pi (IR remote test passed)

- [x] **T04** Smoke test — completed
  - Full FoV fix applied: `raw={"size": (3280, 2464)}`
  - Rotation confirmed: local Pi uses `"hflip"`, not `"hvflip"`
  - Both Pis confirmed NoIR modules (uniform red cast + IR remote test)
  - AWB disabled + manual ColourGains calibration needed — handled in Phase 2

### Phase 2 — Calibration

- [ ] **T05** `calibrate.py` — calibration sweep
  - `get_bucket(brightness) -> int`
  - `needs_calibration(bucket) -> bool`
  - `run_sweep(bucket)` — iterate ISO × shutter × colour_gains, score each, save best to `calibration.toml`
  - `load_params(bucket) -> dict`

- [ ] **T06** Test calibration sweep on local Pi — verify `calibration.toml` is written correctly

### Phase 3 — Image processing & orchestration

- [ ] **T07** `image.py` — Pillow post-processing
  - `process(img, config) -> PIL.Image`
  - Crop, add location name + timestamp annotation, save as JPG
  - Write `latest.jpg` and timestamped archive file

- [ ] **T08** `snapshot.py` — main entry point
  - Parse args (`--calibrate` flag)
  - Meter light → get bucket → load or run calibration
  - Capture → process → save → upload
  - Clean error handling throughout

### Phase 4 — Web UI

- [ ] **T09** `web/app.py` — FastHTML web UI (now has real data to show)
  - Serve `latest.jpg`
  - Show current calibration state (bucket, params, last updated)
  - Show last capture timestamp
  - **Setup page**: display latest frame with click-to-mark region tool for
    `light_region` and `white_reference_region` — replaces standalone `find_region.py`

- [ ] **T10** `find_region.py` — retired as standalone script once T09 setup page exists
  - Until T09 is done, use a temporary CLI version to identify region coordinates

### Phase 5 — Upload

- [ ] **T11** `upload.py` — remote file transfer
  - FTP or SFTP depending on `config.toml` + env vars
  - Upload latest archive image after each successful capture

### Phase 6 — Deployment

- [ ] **T12** Cabin Pi OS upgrade plan — Debian 10 → 12/13 (remote, headless, needs rollback strategy)
- [ ] **T13** Deployment to cabin Pi — copy code, config, set up cron job

---

## Open questions

1. **FTP vs SFTP** — does the destination server support SFTP? Prefer SFTP for security.
2. **Cabin Pi OS upgrade** — needs a safe remote upgrade strategy before new code can be deployed.
3. **Cron schedule** — how often should snapshots run? (Old code implied hourly.)
4. **Web UI hosting** — does the FastHTML app run on the Pi itself, or somewhere else?
5. **`white_region`** — exact coordinates TBD, finalized in T09 setup page.
6. ~~**Camera module confirmation**~~ — resolved: both Pis confirmed NoIR (IR remote test).
7. ~~**Per-device transform config**~~ — resolved: `rotation` field in `config.toml`,
   local Pi = `"hflip"`, cabin Pi TBD when accessible.
