import tomllib
from picamera2 import Picamera2
from libcamera import Transform

TRANSFORMS = {
    "hvflip":   Transform(vflip=True, hflip=True),
    "vflip":    Transform(vflip=True),
    "hflip":    Transform(hflip=True),
    "none":     Transform(),
}

def load_config(path="config.toml"):
    with open(path, "rb") as f:
        return tomllib.load(f)

def main():
    cfg = load_config()
    
    rotation = cfg["camera"]["rotation"]
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

if __name__ == "__main__":
    main()
