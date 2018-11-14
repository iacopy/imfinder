from itertools import combinations
import cv2
import os
import numpy as np
import sys


EX_USAGE = 64  # command line usage error
EX_DATAERR = 65  # data format error
EX_NOINPUT = 66  # cannot open input


def calc_images_diff_ratio(im1, im2, method=cv2.TM_CCOEFF_NORMED):
    """
    Perform template matching with given method and return the rect where the small
    image is found, but only if the threshold is reached, else return None.

    :param small_images: the "probe" image(s) to search for
    :param large_image: the image to search within
    :param method: the match template method
    :param threshold: float [0, 1]
    """
    if isinstance(im1, str):
        im1 = cv2.imread(im1, 0)
    if isinstance(im2, str):
        im2 = cv2.imread(im2, 0)

    assert im1.shape == im2.shape, 'Images have different sizes!'

    w, h = im1.shape[::-1]
    # Apply template matching
    res = cv2.matchTemplate(im1, im2, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    x, y = top_left
    return dict(ratio=max_val, pos=(x, y, w, h))


def calc_images_diff_ratio_more_methods(im1, im2,
        methods=(cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR, cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED),
        func=np.mean):
    ratios = []
    for i, method in enumerate(methods):
        try:
            ratio = calc_images_diff_ratio(im1, im2, method=method)['ratio']
        except AssertionError as err:
            print(method, err)
        else:
            print(i, ratio)
            ratios.append(ratio)
    if ratios:
        return func(ratios)
    return np.nan


def report_ratio_in_new_collage(im1, im2, ratio, dst):
    """Make and save collage using the 2 images and adding a caption containing the given `ratio`.
    """
    im1 = cv2.imread(im1, 0)
    im2 = cv2.imread(im2, 0)
    total_w = im1.shape[1] + im2.shape[1]
    font = cv2.FONT_HERSHEY_SIMPLEX
    caption = np.ones((40, total_w)) * 255
    caption = cv2.putText(caption, 'ratio = {:.3f}'.format(ratio), (5, 25), font, 0.5, (0, 0, 0))
    collage = np.hstack([im1, im2])
    collage = np.vstack([collage, caption])
    cv2.imwrite(dst, collage)


def main(*args):
    ret = []
    for im1, im2 in combinations(args, 2):
        try:
            ratio = calc_images_diff_ratio_more_methods(im1, im2)
        except AttributeError:
            ratio = -1
            continue

        ret.append((ratio, im1, im2))

        if ratio >= 0.6:
            dirpath = os.path.dirname(im1)
            dirpath, f_im1 = os.path.split(im1)
            name1, ext1 = os.path.splitext(f_im1)
            dirpath, f_im2 = os.path.split(im2)
            name2, ext2 = os.path.splitext(f_im2)
            dst_fname = '{:.3f}_{}_vs_{}{}'.format(ratio, name1, name2, ext1)
            dst = os.path.join(dirpath, dst_fname)
            report_ratio_in_new_collage(im1, im2, ratio, dst)

    ret.sort()
    for ratio, im1, im2 in ret:
        if ratio >= 0.6:
            print('{im1} vs {im2}: {r}'.format(im1=im1, im2=im2, r=ratio))


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 1:
        dirpath = args[0]
        files = [os.path.join(dirpath, filename) for filename in os.listdir(dirpath)]
    else:
        files = args
    main(*files)
