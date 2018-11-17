import os
import sys

import cv2


EX_USAGE = 64  # command line usage error
EX_DATAERR = 65  # data format error
EX_NOINPUT = 66  # cannot open input
EX_NOUSER = 67  # addressee unknown
EX_NOHOST = 68  # host name unknown
EX_UNAVAILABLE = 69  # service unavailable
EX_SOFTWARE = 70  # internal software error
EX_OSERR = 71  # system error (e.g., can't fork)
EX_OSFILE = 72  # critical OS file missing
EX_CANTCREAT = 73  # can't create (user) output file
EX_IOERR = 74  # input/output error
EX_TEMPFAIL = 75  # temp failure; user is invited to retry
EX_PROTOCOL = 76  # remote error in protocol
EX_NOPERM = 77  # permission denied
EX_CONFIG = 78  # configuration error

DEFAULT_THRESHOLD = 0.99

imread = cv2.imread


def bool_find(small_image, large_image,
              method=cv2.TM_CCOEFF_NORMED, threshold=DEFAULT_THRESHOLD):
    """
    Utility function, useful if one want to know only *if* an image
    is contained in another one.

    :param small_image:
    :param large_image:
    :param method:
    :param threshold:
    :return: bool
    """
    for res in find_small_in_large(
        small_image, large_image, method, threshold):
        if res:
            return True
    return False


def find_small_in_large(small_images, img,
                        method=cv2.TM_CCOEFF_NORMED,
                        threshold=DEFAULT_THRESHOLD):
    """
    Perform template matching with given method and return the rect where the small
    image is found, but only if the threshold is reached, else return None.

    :param small_images: the "probe" image(s) to search for
    :param large_image: the image to search within
    :param method: the match template method
    :param threshold: float [0, 1]
    """
    if not isinstance(small_images, (list, tuple)):
        small_images = [small_images]

    for template in small_images:
        #template = cv2.imread(small_image_path, 0)
        if template is None:
            #print('INPUT ERROR: %s and/or %s do not exist!' % (small_image_path, large_image_path))
            sys.exit(EX_NOINPUT)

        w, h = template.shape[: 2]

        img2 = img.copy()
        img = img2.copy()

        # Apply template matching
        res = cv2.matchTemplate(img, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold:
            # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc
            x, y = top_left
            yield x, y, w, h
        else:
            yield None


def find_small_in_image_with_multiple_results(template_gray, img_rgb,
                                              threshold=DEFAULT_THRESHOLD):
    """
    This is a demo which shows the result of a match template
    search with multiple matches of a single sub image.

    :param template_gray: the "probe" image
    :param img_rgb: the image to search within
    :param threshold: float
    :return: None
    """
    import numpy as np

    small_filename = os.path.split(template_gray)[1]
    large_filename = os.path.split(img_rgb)[1]
    dst_filename = '{}_in_{}'.format(small_filename, large_filename)

    try:
        img_rgb = cv2.imread(img_rgb)
    except Exception as err:
        # is already an image
        print(err)

    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    try:
        template = cv2.imread(template_gray, 0)
    except Exception as err:
        # is already an image
        print(err)
        template = template_gray

    h, w = template.shape[: 2]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    # WARNING: this seems broken, do not fit correct position actually
    for pt in zip(*loc[::-1]):
        # pt is the topleft coordinate of the current match
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 1)
        yield pt

    cv2.imwrite(dst_filename, img_rgb)  # demo


def main(template_image_path, image_path, **kwargs):
    template = imread(template_image_path, 0)
    image = imread(image_path, 0)
    box = list(find_small_in_large(template, image, **kwargs))
    mul = list(find_small_in_image_with_multiple_results(template_image_path,
                                                         image_path, **kwargs))
    print(len(box), len(mul))
    print(box)
    print(bool_find(template, image, **kwargs))
    return 0  # temporary


if __name__ == '__main__':
    try:
        small, large = sys.argv[1:]
    except ValueError:
        exit_code = EX_USAGE
        print('USAGE ERROR: invalid argument!')
        print('Usage: $ python imfinder.py <small_image_path> <large_image_path>')
    else:
        exit_code = main(small, large, threshold=0.98)
    sys.exit(exit_code)
