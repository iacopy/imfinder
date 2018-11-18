"""
Crop an image via cli.
"""

from cv2 import imread
from cv2 import imwrite
import sys


def cut_image(image_filepath, box, dst_filepath):
    x_start, y_start, width, height = box
    x_stop, y_stop = x_start + width, y_start + height
    image = imread(image_filepath)
    return imwrite(
        dst_filepath,
        image[y_start: y_stop, x_start: x_stop]
    )


def main():
    image_filepath = sys.argv[1]
    box = [int(val) for val in sys.argv[2:6]]
    dst_filepath = sys.argv[6]

    res = cut_image(image_filepath, box, dst_filepath)
    sys.exit(not res)


if __name__ == '__main__':
    main()
