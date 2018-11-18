"""
Crop an image via cli.
"""

from cv2 import imread
from cv2 import imwrite

import os
import random
import sys


def cut_image(image_filepath, box, dst_filepath=None):
    if dst_filepath is None:
        pre, ext = os.path.splitext(image_filepath)
        dst_filepath = pre + '_cut' + ext

    x_start, y_start, width, height = box

    image = imread(image_filepath)

    h, w = image.shape[: 2]
    if x_start < 0:
        x_start = w + x_start
    if y_start < 0:
        y_start = h + y_start

    x_stop, y_stop = x_start + width, y_start + height

    return imwrite(
        dst_filepath,
        image[y_start: y_stop, x_start: x_stop]
    )


def cut_image_random(image_filepath, crop_width=100, crop_height=100, dst_filepath=None):
    if dst_filepath is None:
        pre, ext = os.path.splitext(image_filepath)
        dst_filepath = pre + '_cut' + ext
    image = imread(image_filepath)
    h, w = image.shape[: 2]
    x_start = random.randrange(w - crop_width)
    y_start = random.randrange(h - crop_height)
    x_stop = x_start + crop_width
    y_stop = y_start + crop_height
    imwrite(dst_filepath, image[y_start: y_stop, x_start: x_stop])
    return x_start, y_start, crop_width, crop_height



def main():
    image_filepath = sys.argv[1]
    box = [int(val) for val in sys.argv[2:6]]
    dst_filepath = sys.argv[6]

    res = cut_image(image_filepath, box, dst_filepath)
    sys.exit(not res)


if __name__ == '__main__':
    main()
