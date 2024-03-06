import piexif
import pyexiv2 as pyexiv2
from PIL import Image


def __print_metadata(filename):
    im = Image.open(filename)
    exif_dict = piexif.load(im.info["exif"])
    print(exif_dict)


def five_stars_to_file(filename):
    if not can_modify_meta_data:
        return

    print(filename)
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
    print("5 stars to " + filename)


def has_image_file_ending(filename):
    return filename.endswith('.jpg') or \
        filename.endswith('.jpeg') or \
        filename.endswith('.png') or \
        filename.endswith('.giv') or \
        filename.endswith('.mp4')


def can_modify_meta_data(filename):
    return filename.endswith('.jpg') or \
        filename.endswith('.jpeg')


def is_filename_in_ignore_list(filename):
    if "trash" in filename.lower():
        return True
    if filename.startswith("."):
        return True
    return False


def is_path_in_ignore_list(path):
    if "Sent" is path:
        return True
    if "Private" is path:
        return True
    if "/." in path:
        return True
    return False
