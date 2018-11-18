"""
Create a markers directory where to put N template images for N targets.
You can have only 1 template for 1 target.

root/
    pippo1.jpg
    pippo2.jpg
    pluto1.jpg
    pluto2.jog
    markers_dir/
        template_pippo.jpg
        template_pluto.jpg
"""
import os
import sys

import cv2

from imfinder import bool_find


class Marker:
    def __init__(self, name, image_filepath):
        self.name = name
        self.image = cv2.imread(image_filepath, 0)
        assert self.image is not None

    def __repr__(self):
        return 'Marker({})'.format(self.name)


def get_markers_images(dirpath, markers_dirname):
    ret = []
    markers_dirpath = os.path.join(dirpath, markers_dirname)
    for filename in os.listdir(markers_dirpath):
        if not filename.startswith('.'):
            name, ext = os.path.splitext(filename)
            template_image_path = os.path.join(markers_dirpath, filename)
            marker = Marker(name, template_image_path)
            ret.append(marker)
    return ret

def decide(image_filepath, markers):
    image_gray = cv2.imread(image_filepath, 0)
    img_rgb = cv2.imread(image_filepath)
    # image_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    for marker in markers:
        try:
            if bool_find(marker.image, image_gray, threshold=0.9):
                return marker.name
        except cv2.error as err:
            assert "_img.size().height <= _templ.size().height && _img.size().width <= _templ.size().width in function 'matchTemplate'" in str(err)


def dispatch(dirpath, markers_dirname='templates'):
    ret = {}
    if markers_dirname not in os.listdir(dirpath):
        print('ERROR: Please create a "{}" directory with marker images.'.format(markers_dirname))
        return

    markers = get_markers_images(dirpath, markers_dirname)
    print(len(markers), 'markers found:', markers)

    for filename in os.listdir(dirpath):
        if filename.startswith('.'):
            continue

        image_filepath = os.path.join(dirpath, filename)
        if not os.path.isfile(image_filepath):
            continue

        res = decide(image_filepath, markers)
        if res:
            print(filename, '->', res)
            ret[filename] = res
    return ret


def main(dirpath, markers_dirname='templates'):
    # TODO: actual file dispatching
    pass


if __name__ == '__main__':
    dispatch(sys.argv[1])
