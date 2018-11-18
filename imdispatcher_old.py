"""
Implementazione vecchia alternativa a imdispatcher.py

Più prolissa, quindi da preferire l'altra.
C'e' l'opzione recursive in più, per ora.

    python imdispatcher.py <template-dir> <search-dir> <dst-dir> [--threshold] [--dry_run]
"""

# TODO: log ingombrante da togliere

from cv2 import error
from imfinder import bool_find, imread
from os import sys, walk
from os.path import abspath, basename, exists, isdir, join, split, splitext
import argparse
import datetime
import re
import shutil


WRONG_IMAGE_SIZE = 'wrong_image_size'
NON_MATCHING_PATHS = 'non-matching_path'
INVALID_IMAGES = 'invalid_image'
UNCLASSIFIED_IMAGES = 'unclassified_image'
DISPATCHED_IMAGES = 'dispatched_images'
TEMPLATE_MATCHING_ERROR = 'template_matching_error'


def move(src, dst, dry_run=False):
    assert exists(dst), 'dst="{}" does not exist'.format(dst)
    assert isdir(dst), 'dst="{}" is not a directory'.format(dst)
    src_dir_path, src_file_name = split(src)
    dst_file_name = src_file_name
    while True:
        dst_file_path = join(dst, dst_file_name)
        if exists(dst_file_path):
            name, ext = splitext(dst_file_name)
            dst_file_name = name + '+' + ext
        else:
            break

    if not dry_run:
        shutil.move(src, dst_file_path)

    return dst_file_path


def process_templates(templates_dirpath):
    print('process_templates', templates_dirpath)
    res = []
    for dirpath, dirs, files in walk(templates_dirpath):
        for file_name in files:
            if not file_name.startswith('template'):
                continue

            file_path = join(dirpath, file_name)
            template = imread(file_path, 0)
            assert template is not None, 'Invalid template image: {}'.format(file_path)
            label = dirpath[len(templates_dirpath):]
            res.append((file_path, template, label))
    return res


def log(start_datetime, file_path, result_flag):
    dt = start_datetime.isoformat()[:-7].replace(':', '-')
    file_name = u'image_dispatcher_{}_{}.log'.format(
        dt, result_flag)

    now_str = datetime.datetime.now().isoformat()
    with open(file_name, 'a') as fp:
        fp.write(u'{}: {}\n'.format(now_str, file_path.encode('utf-8')))


def main(templates_dirpath, root, dst,
        matching_threshold=0.9,
        dry_run=False,
        recursive=False,
        file_path_filter='jpg$|png$',
        image_size=None,
        log_file_path='log.txt'):

    res = {
        DISPATCHED_IMAGES: [],
        INVALID_IMAGES: [],
        NON_MATCHING_PATHS: [],
        UNCLASSIFIED_IMAGES: [],
        WRONG_IMAGE_SIZE: [],
    }


    if image_size:
        image_shape = tuple(reversed(image_size))

    root = abspath(root)
    dst = abspath(dst)
    file_path_compiled_regexp = re.compile(file_path_filter, re.IGNORECASE)
    n_dirs = n_files = n_images = n_filtered_images = n_dispatched = 0

    templates_data = process_templates(templates_dirpath)
    print('{} templates found'.format(len(templates_data)))

    start_datetime = datetime.datetime.now()

    try:
        for dirpath, dirs, files in walk(root, recursive=recursive):
            if dirpath == dst or dirpath == templates_dirpath:
                # we are entering in the dst dir! skip please
                print('SKIPPING dst or templates directory', dirpath)
                continue
            if basename(dirpath).startswith('dispatched'):
                print('skip', dispatched)
                continue

            print('{:,} dirs/{:,} files: {}'.format(n_dirs, n_files, dirpath))
            n_dirs += 1
            for file_name in files:
                n_files += 1
                file_path = join(dirpath, file_name)
                if not re.search(file_path_compiled_regexp, file_path):
                    #res[NON_MATCHING_PATHS].append(file_path)
                    log(start_datetime, file_path, NON_MATCHING_PATHS)
                    continue

                # Read image to classify
                image = imread(file_path, 0)

                if image is None:
                    #res[INVALID_IMAGES].append(file_path)
                    log(start_datetime, file_path, INVALID_IMAGES)
                    #print('   invalid image')
                    continue

                n_images += 1
                if image_size and image.shape != image_shape:
                    log(start_datetime, file_path, WRONG_IMAGE_SIZE)
                    continue

                n_filtered_images += 1

                dispatched = False
                for template_path, template, dest in templates_data:
                    # Template matching
                    # print('{} vs {} ({})'.format(template_path, file_path, matching_threshold))
                    try:
                        r = bool_find(template, image, threshold=matching_threshold)
                    except error as err:
                        log(start_datetime, file_path, TEMPLATE_MATCHING_ERROR)
                        print('Template matching error')
                        print(err)
                        r = False

                    if r:
                        dt_str = datetime.datetime.now().isoformat()[:-7]
                        dst_dir = join(dst, dest)

                        dst_file_path = move(file_path, dst_dir, dry_run=dry_run)

                        dispatched = True
                        n_dispatched += dispatched

                        res[DISPATCHED_IMAGES].append((file_path, dst_file_path, basename(template_path)))
                        msg = u'{}: "{}" contains "{}": >> {}'.format(
                            dt_str, file_path, basename(template_path), dst_dir)
                        print(msg)
                        print('{:,} moved/{:,} candidates/{:,} images/{:,} files'.format(
                            n_dispatched, n_filtered_images, n_images, n_files))

                        with open(log_file_path, 'a') as fp:
                            fp.write(u'{}\n'.format(msg))

                        log(start_datetime, file_path, DISPATCHED_IMAGES)

                        break

                if not dispatched:
                    log(start_datetime, file_path, UNCLASSIFIED_IMAGES)
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    #res[UNCLASSIFIED_IMAGES].append(file_path)

    except KeyboardInterrupt:
        print('Interrupted by user.')

    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Image dispatcher')
    parser.add_argument('query', help='query image path to search for')
    parser.add_argument('root', default=u'.',
                        help='root directory to search in [default=%(default)s]')
    parser.add_argument('dst', default=u'../dispatched-images',
                        help='directory to move images into [default="%(default)s"]')
    parser.add_argument('--threshold', type=float, default=0.9,
                        help='template matching threshold [default=%(default)s]')
    parser.add_argument('--recursive', action='store_true', default=False,
                        help='search recursively inside `root` [default=%(default)s]')
    parser.add_argument('--dry_run', action='store_true', default=False,
                        help='do not actually move files [default=%(default)s]')
    parser.add_argument('--logfile', default='log.txt',
                        help='log file path [default=%(default)s]')
    parser.add_argument('--log', dest='loglevel', default='DEBUG',
                        help='Set the logging level [default=%(default)s]')
    args = parser.parse_args()
    print(args)
    results = main(args.query, args.root, args.dst, matching_threshold=args.threshold,
        recursive=args.recursive, dry_run=args.dry_run, log_file_path=args.logfile)

    print('{:,} images dispatched'.format(len(results[DISPATCHED_IMAGES])))

    sys.exit(0)
