import tomllib
from picamera2 import Picamera2
from libcamera import Transform
import numpy as np
from PIL import Image

TRANSFORMS = {
    "hvflip":   Transform(vflip=True, hflip=True),
    "vflip":    Transform(vflip=True),
    "hflip":    Transform(hflip=True),
    "none":     Transform(),
}

def load_config(path="config.toml"):
    with open(path, "rb") as f:
        return tomllib.load(f)

def meter_light(arr, light_region):
    # slice the light_region patch
    x1, y1, x2, y2 = light_region
    patch = arr[y1:y2, x1:x2]
    # np.mean() -> return the float
    intensity = np.mean(patch)
    return intensity
    
def meter_white(arr,white_region):
    # slice the white_region patch
    x1, y1, x2, y2 = white_region
    patch = arr[y1:y2, x1:x2]
    r_arr = patch[:, :, 0] # Red
    g_arr = patch[:, :, 1] # Green
    b_arr = patch[:, :, 2] # Blue
    r = np.mean(r_arr)
    g = np.mean(g_arr)
    b = np.mean(b_arr)
    return (float(r/g), float(r/b))

def capture(cam, params: dict):
    cam.set_controls(params) # applies ISO, shutter speed, colour gains
    arr = cam.capture_array()
    return Image.fromarray(arr)

def main():
    cfg = load_config()
    
    rotation = cfg["camera"]["rotation"]
    raw = tuple(cfg["camera"]["raw_resolution"])
    resolution = tuple(cfg["camera"]["resolution"])
    latest_path = cfg["image"]["latest_path"]
    light_region = cfg["metering"]["light_region"]
    white_region = cfg["metering"]["white_region"]

    transform = TRANSFORMS[rotation]
    
    cam = Picamera2()
    config = cam.create_still_configuration(
        raw={"size": raw},
        main={"size": resolution},
        transform=transform)
    cam.configure(config)

    cam.start()
    cam.set_controls({"AwbEnable": False, "ColourGains": (1.0, 1.0)})
    arr = cam.capture_array()
    print(f'meter_light: {meter_light(arr, light_region)}')
    print(f'meter_white: {meter_white(arr, white_region)}')   
    cam.capture_file(latest_path) 
    cam.close()

if __name__ == "__main__":
    main()
