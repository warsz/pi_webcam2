# Session log

## Completed this session

- Confirmed both Pis are NoIR modules (IR remote test + green cast in daylight image)
- Viewed first daylight image — correct rotation, green cast confirmed
- `camera.py`: added try/except around picamera2 import so calibrate.py can be imported on Mac
- `calibrate.py`: completed `get_bucket()`, `needs_calibration()`, `read_file()`
- `calibrate.py`: `run_sweep()` — params extracted from cfg, triple loop skeleton in place
- Refactored `read_calibration()` into generic `read_file()` used for both TOML files
- Fixed: `needs_calibration` check moved to `main()`, not inside `run_sweep()`

## Known issues / broken stuff

- `run_sweep()` loop has typo `inn` on line 13 — fix before running
- `cam = "dummy_cam"` placeholder in `main()` — camera not wired up in calibrate.py yet
- `brightness = meter_light(...)` still commented out in `main()`
- camera import still commented out (line 2) — needed on Pi

## Next step

**Fill in capture + variance scoring inside `run_sweep()` loop**
- Fix typo `inn` → `in` on line 13
- Mock capture return (numpy array) for Mac testing
- Add `np.var(arr)` as score, track best `(i, s, c, score)`
- Write best params to `calibration.toml` after loop
