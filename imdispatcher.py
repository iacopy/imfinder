"""
dispatch:

Create N templates directory where to put N kind of images.
Each template directory is allowed to contain several template images
sice the same kind of image could have different presentation
(e.g. app changing layout or gui or pages)

root/
    pippo1.jpg
    pippo2.jpg
    pluto1.jog
    pluto2.jpg
    template_pippo/
        template__pippo.png
    template_pluto/
        template__pluto_a.png
        template__pluto_b.png


dispatch_legacy:

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
import shutil
import sys

import cv2

from imfinder import bool_find


class Marker:
    def __init__(self, name, image_filepath):
        self.name = name
        self.dst = name
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


class Template:
    def __init__(self, image_filepath):
        dirpath, filename = os.path.split(image_filepath)
        name = os.path.splitext(filename)[0]
        self.name = name
        self.dst = dirpath
        self.image = cv2.imread(image_filepath, 0)
        assert self.image is not None

    def __repr__(self):
        return 'Template({}[{}])'.format(self.name, self.image.shape)


def get_templates_dirs(dirpath, templates_dirs):
    ret = []
    for dirname in templates_dirs:
        templates_dirpath = os.path.join(dirpath, dirname)
        for filename in os.listdir(templates_dirpath):
            if filename.startswith('.') or not filename.startswith('template__'):
                continue

            template_image_path = os.path.join(templates_dirpath, filename)
            template = Template(template_image_path)
            ret.append(template)
    return ret


def decide(image_filepath, templates):
    image_gray = cv2.imread(image_filepath, 0)
    img_rgb = cv2.imread(image_filepath)
    # image_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    for template in templates:
        try:
            if bool_find(template.image, image_gray, threshold=0.95):
                return template.dst
        except cv2.error as err:
            assert "_img.size().height <= _templ.size().height && _img.size().width <= _templ.size().width in function 'matchTemplate'" in str(err)


def dispatch_legacy(dirpath, markers_dirname='templates'):
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


def dispatch(dirpath, templates_dirs, action=None):
    ret = {}
    templates = get_templates_dirs(dirpath, templates_dirs)
    print(templates)
    filenames = [filename for filename in os.listdir(dirpath) if not filename.startswith('.') \
        and os.path.isfile(os.path.join(dirpath, filename))]
    filenames.sort()
    n_filenames = len(filenames)
    for i, filename in enumerate(filenames):
        image_filepath = os.path.join(dirpath, filename)

        print('{:,}/{:,} ({:.01%}) {}'.format(i, n_filenames, i / n_filenames, filename))
        dst = decide(image_filepath, templates)
        if not dst:
            continue

        print(filename, '->', dst)
        ret[filename] = dst

        if action:
            try:
                action(image_filepath, dst)
            except Exception as err:
                print(err)
    return ret


def main(dirpath, templates_dirs):
    print('main({}, {}'.format(dirpath, templates_dirs))
    dispatch(dirpath, templates_dirs, action=shutil.move)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
