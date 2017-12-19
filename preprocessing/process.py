# USAGE
# python scan.py --image images/page.jpg

import argparse
import urllib.request
import numpy as np

import crop
from imutils import denoise, hist_equl_color
from imutils import clahe_hist_equal as che

from noteshrink import notescan_main

import cv2


def process(image):
    # document, cropped = crop.find_document(image)
    document, cropped = image, False

    # TODO: if cropped look for text in document if there is some text continue if there are no continue with stating image
    if cropped:
        pass

    # cv2.namedWindow('document', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('document', 1000,1000)
    # cv2.imshow("document", document)
    #
    # cv2.namedWindow('document3', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('document3', 1000,1000)
    # cv2.imshow("document3", che(che(che(document))))
    #
    # cv2.namedWindow('document3+DENOISE', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('document3+DENOISE', 1000,1000)
    # cv2.imshow("document3+DENOISE", che(che(denoise(che(document)))))
    #
    # cv2.namedWindow('document3+2DENOISE', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('document3+2DENOISE', 1000,1000)
    # cv2.imshow("document3+2DENOISE", denoise(che(che(denoise(che(document))))))
    #
    # cv2.namedWindow('document3+3DENOISE', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('document3+3DENOISE', 1000,1000)
    # cv2.imshow("document3+3DENOISE", denoise(che(che(denoise(che(denoise(document)))))))
    #
    # cv2.waitKey(0)

    filenames = []

    cv2.imwrite('temp/original.jpg', image)
    filenames.append('temp/original.jpg')
    if cropped:
        filenames.append('temp/cropped.jpg')
        cv2.imwrite('temp/cropped.jpg', document)
    #
    filenames.append('temp/out11d1.jpg')
    filenames.append('temp/out111.jpg')
    filenames.append('temp/out11.jpg')

    print("Writing double clahe_hist_equal")
    cv2.imwrite('temp/out11.jpg', che(che(document)))
    print("Writing triple clahe_hist_equal")
    cv2.imwrite('temp/out111.jpg', che(che(che(document))))
    print("Writing triple clahe_hist_equal + denoising")
    cv2.imwrite('temp/out11d1.jpg', che(che(denoise(che(document)))))
    # print("Writing triple clahe_hist_equal + triple denoising")
    # dccdcd = denoise(che(che(denoise(che(denoise(document))))))
    # cv2.imwrite("temp/outd11d1d.jpg", dccdcd)

    # cv2.imwrite('temp/step-6.jpg', dccdcd)

    shrink(filenames)


def shrink(filenames):
    # filenames = ["temp/out11d1.jpg", "temp/out111.jpg", "temp/out11.jpg", "temp/out.jpg"]
    options = argparse.Namespace(basename='page', filenames=filenames, global_palette=False, num_colors=8, pdf_cmd='convert %i %o', pdfname='out/output.pdf', postprocess_cmd=None, postprocess_ext='_post.png', quiet=False, sample_fraction=0.05, sat_threshold=0.2, saturate=True, sort_numerically=True, value_threshold=0.25,
                                 white_bg=True)
    notescan_main(options)


def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # return the image
    return image


import os

A_PATH = os.path.dirname(os.path.abspath(__file__))


def tg_process(url):
    image = url_to_image(url)

    # document, cropped = crop.find_document(image)
    document, cropped = image, False

    filenames = []

    cv2.imwrite(A_PATH + '/temp/original.jpg', image)
    filenames.append(A_PATH + '/temp/original.jpg')
    if cropped:
        filenames.append(A_PATH + '/temp/cropped.jpg')
        cv2.imwrite(A_PATH + '/temp/cropped.jpg', document)

    filenames.append(A_PATH + '/temp/out11d1.jpg')
    filenames.append(A_PATH + '/temp/out111.jpg')
    filenames.append(A_PATH + '/temp/out11.jpg')

    print("Writing double clahe_hist_equal")
    cv2.imwrite(A_PATH + '/temp/out11.jpg', che(che(document)))
    print("Writing triple clahe_hist_equal")
    cv2.imwrite(A_PATH + '/temp/out111.jpg', che(che(che(document))))
    print("Writing triple clahe_hist_equal + denoising")
    cv2.imwrite(A_PATH + '/temp/out11d1.jpg', che(che(denoise(che(document)))))

    shrink(filenames)

    return [A_PATH + '/out/' + f for f in ["output.pdf", "page0000.png",
                                               "page0001.png", "page0002.png",
                                               "page0003.png"]]


if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
                    help="Path to the image to be scanned")
    args = vars(ap.parse_args())

    # load the image and compute the ratio of the old height
    # to the new height, clone it, and resize it
    image = cv2.imread(args["image"])
    # image = cv2.imread("4.jpg")

    process(image)
