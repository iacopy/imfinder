# Imfinder

Just search an image inside another with python and opencv.


## Manual test and usage

Crop a piece from test image (the first green check mark):

    $ python imcut.py test/test.png 300 200 100 94 test/test_check.png

Find cropped check mark (and higlight it on new image):

    $ python imfinder test/test_check.png test/test.png
