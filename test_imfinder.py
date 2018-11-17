from imcut import cut_image
from imfinder import cv2, bool_find, find_small_in_large, find_small_in_image_with_multiple_results


def test_imcut_and_search():
    """
    Crop a portion of a test image and then search the cropped image
    within the source.
    """
    large_fpath = 'test/test.png'
    cut_fpath = 'test/test_cut.png'
    box = (300, 200, 400, 294)

    # obtain the cut image
    # (produce a test "artifact")
    cut_image(large_fpath, box, cut_fpath)

    template = cv2.imread(cut_fpath, 0)
    assert template is not None

    large = cv2.imread(large_fpath, 0)
    assert bool_find(template, large)

    res = find_small_in_large(template, large, threshold=0.98)
    assert box[: 2] in list(res)

    # NB: the "highlight" flag produce another test "artifact"
    # (the image with the found rectangle highlighted)
    res = find_small_in_image_with_multiple_results(
        cut_fpath, large_fpath, threshold=0.98,
        highlight=True)
    assert box[: 2] in list(res)
