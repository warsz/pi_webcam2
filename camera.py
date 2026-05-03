from picamera2 import Picamera2
from libcamera import Transform

# we just want to take one image and store it as latest.jpg in this folder

def main():
    # 1. open the camera: IMX219
    cam = Picamera2()
    # 2. configure rotation 180 degrees
    config = cam.create_still_configuration(transform=Transform(vflip=True, hflip=True))
    cam.configure(config)

    # 3. capture an image
    cam.start()
    # 4. save the image
    cam.capture_file("latest.jpg") 
    # 5. close
    cam.close()

if __name__ == "__main__":
    main()
