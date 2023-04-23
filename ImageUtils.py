import piexif
import pyexiv2 as pyexiv2
from PIL import Image


def printMetadata(filename):
    im = Image.open(filename)
    exif_dict = piexif.load(im.info["exif"])
    print(exif_dict)


def fiveStarsToFile(filename):
    with open(filename, 'rb+') as f:
        with pyexiv2.ImageData(f.read()) as img:
            changes_rating = {'Exif.Image.Rating': 5}
            changes_rating_percent = {'Exif.Image.RatingPercent': 99}
            img.modify_exif(changes_rating)
            img.modify_exif(changes_rating_percent)
            f.seek(0)
            f.truncate()
            f.write(img.get_bytes())
        f.seek(0)
        with pyexiv2.ImageData(f.read()) as img:
            result = img.read_iptc()

    printMetadata(filename)
