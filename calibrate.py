from math import floor, log2
import tomllib

def get_bucket(brightness): # int
    cfg_bucket_count = 8
    bucket = floor(log2(brightness + 1))
    return min(bucket, cfg_bucket_count -1)

def needs_calibration(bucket):
    bkt = f'bucket_{bucket}'
    try:
        with open("calibration.toml", "rb") as f:
            cal = tomllib.load(f)
            return bkt not in cal
    except FileNotFoundError:
        return True

def main():
    brs = [0, 5, 10, 50, 100, 150, 200, 255]
    for b in brs:
        bkt = get_bucket(b)
        print(f'brightness={b} ->  bucket={bkt}')
    print(needs_calibration(0))
    print(needs_calibration(7))

if __name__=="__main__":
    main()
