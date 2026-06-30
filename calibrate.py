from math import floor, log2
from itertools import product
# from camera import load_config, capture, meter_white, meter_light
import tomllib

def run_sweep(bkt, cam, cfg): 
    # get sweep params from cfg
    isos = cfg["calibration"]["sweep_iso"]
    shutters = cfg["calibration"]["sweep_shutter_us"]
    c_gains = cfg["calibration"]["sweep_colour_gains"]
    # loop over all combinations
    for i in isos:
        for s in shutters:
            for c in c_gains:
                # capture
                # score by variance
                # track best
    # once finished write to calibration.toml
    print("test")

def get_bucket(brightness):
    cfg_bucket_count = 8
    bucket = floor(log2(brightness + 1))
    return min(bucket, cfg_bucket_count -1)

def needs_calibration(bkt):
    cal = read_file("calibration.toml")
    return f'bucket_{bkt}' not in cal

def read_file(file_name):
    try:
        with open(file_name, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        return {}

def main():
    cfg = read_file("config.toml")  # read config.toml once
    cam = "dummy_cam" # open_camera(cfg)          # sets up cam once
    # brightness = meter_light(...)

    brs = [0, 5, 10, 50, 100, 150, 200, 255]
    for b in brs:
        bkt = get_bucket(b)
        print(f'brightness={b} ->  bucket={bkt}')
        if needs_calibration(bkt):
            run_sweep(bkt, cam, cfg)
    # print(needs_calibration(0))
    # print(needs_calibration(7))

if __name__=="__main__":
    main()
