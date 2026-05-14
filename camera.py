import tomllib
from picamera2 import Picamera2
from libcamera import Transform
import numpy as np

TRANSFORMS = {
    "hvflip":   Transform(vflip=True, hflip=True),
    "vflip":    Transform(vflip=True),
    "hflip":    Transform(hflip=True),
    "none":     Transform(),
}

def load_config(path="config.toml"):
    with open(path, "rb") as f:
        return tomllib.load(f)

def meter_light(cfg: dict):
    
    
    # start camera
    cam = Picamera2()
    config = cam.create_still_configuration(
        raw={"size": tuple(cfg["camera"]["raw_resolution"])},
        main={"size": tuple(cfg["camera"]["resolution"])},
        transform=TRANSFORMS[cfg["camera"]["rotation"]]
    )
    cam.configure(config)
    cam.start()
    # capture_array() -> numpy array
    arr = cam.capture_array()
    # slice the light_region patch
    x1, y1, x2, y2 = cfg["metering"]["light_region"]
    patch = arr[y1:y2, x1:x2]
    # np.mean() -> return the float
    intensity = np.mean(patch)
    # close camera
    cam.close()
    return intensity
    

def main():
    cfg = load_config()
    
    rotation = cfg["camera"]["rotation"]
    raw =cfg["camera"]["raw_resolution"]
    resolution = tuple(cfg["camera"]["resolution"])
    latest_path = cfg["image"]["latest_path"]

    transform = TRANSFORMS[rotation]
    
    cam = Picamera2()
    config = cam.create_still_configuration(
        raw={"size": (3280, 2464)},
        main={"size": resolution},
        transform=transform)
    cam.configure(config)

    cam.start()
    cam.capture_file(latest_path) 
    cam.close()

    print(meter_light(cfg))

if __name__ == "__main__":
    main()
