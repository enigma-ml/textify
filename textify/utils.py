# USAGE
# python scan.py --image images/page.jpg


from datetime import datetime
from pathlib import Path
from shutil import rmtree
import argparse
import urllib.request

import numpy as np
from skimage import exposure, img_as_float, img_as_ubyte
from skimage.restoration import denoise_wavelet
import img2pdf
import cv2

from processing import crop
from processing.noteshrink import notescan_main


def get_cropped_pdf(chat_id):
    images = [str(x) for x in get_cropped_images_jpg(chat_id)]
    path = str(get_pdf_path(chat_id)) + "/textify-cropped-{}.pdf".format(datetime.now().strftime("%H%M%S"))
    with open(path, "wb") as f:
        f.write(img2pdf.convert(images))
    return path


def get_originals_pdf(chat_id):
    images = [str(x) for x in get_original_images_jpg(chat_id)]
    path = str(get_pdf_path(chat_id)) + "/textify-originals-{}.pdf".format(datetime.now().strftime("%H%M%S"))
    with open(path, "wb") as f:
        f.write(img2pdf.convert(images))

    return path


def get_scanned_pdf(chat_id):
    images = [str(x) for x in get_scanned_images(chat_id)]
    path = str(get_pdf_path(chat_id)) + "/textify-scanned-{}.pdf".format(datetime.now().strftime("%H%M%S"))
    with open(path, "wb") as f:
        f.write(img2pdf.convert(images))

    return path


def get_user_dir_path(chat_id):
    path = Path('images/{chat_id}'.format(chat_id=chat_id))
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def get_originals_path(chat_id):
    path = get_user_dir_path(chat_id)
    path = path.joinpath('originals')
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        jpg = path.joinpath('jpg')
        jpg.mkdir(parents=True, exist_ok=True)
    return path


def get_scans_path(chat_id):
    path = get_user_dir_path(chat_id)
    path = path.joinpath('scans')
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def get_temp_path(chat_id):
    path = get_user_dir_path(chat_id)
    path = path.joinpath('temp')
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def get_pdf_path(chat_id):
    path = get_user_dir_path(chat_id)
    path = path.joinpath('pdf')
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def get_cropped_path(chat_id):
    path = get_user_dir_path(chat_id)
    path = path.joinpath('cropped')
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        jpg = path.joinpath('jpg')
        jpg.mkdir(parents=True, exist_ok=True)
    return path


def load_and_save_image(chat_id, url):
    try:
        # download and decode image
        resp = urllib.request.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        # save image with unique name
        path = get_originals_path(chat_id)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S%f")
        # write png
        filename = str(path) + '/' + timestamp + '.png'
        cv2.imwrite(filename, image)
        # write jpg
        filename = str(path.joinpath('jpg')) + '/' + timestamp + '.jpg'
        cv2.imwrite(filename, image)
    except Exception as e:
        print("error in save_image", e)
        return False
    return True


def get_original_images(chat_id):
    path = get_originals_path(chat_id)
    images = [x for x in path.glob('*') if x.is_file()]
    return images


def get_original_images_jpg(chat_id):
    path = get_originals_path(chat_id).joinpath('jpg')
    images = [x for x in path.glob('*') if x.is_file()]
    return images


def get_cropped_images(chat_id):
    path = get_cropped_path(chat_id)
    images = [x for x in path.glob('*') if x.is_file()]
    return images


def get_cropped_images_jpg(chat_id):
    path = get_cropped_path(chat_id).joinpath('jpg')
    images = [x for x in path.glob('*') if x.is_file()]
    return images


def get_scanned_images(chat_id):
    path = get_scans_path(chat_id)
    images = [x for x in path.glob('*') if x.is_file()]
    return images


def get_temp_images(chat_id):
    path = get_temp_path(chat_id)
    images = [x for x in path.glob('*') if x.is_file()]
    return images


def delete_images_for_user(chat_id):
    path = Path('images/{chat_id}'.format(chat_id=chat_id))
    if not path.exists():
        return False
    try:
        rmtree(path)
    except Exception as e:
        print("error deleting user ({}) folder".format(chat_id), e)
        return False
    return True


def delete_folder_for_user(chat_id, folder):
    path = Path('images/{chat_id}/{folder}'.format(chat_id=chat_id, folder=folder))
    if not path.exists():
        return False
    try:
        rmtree(path)
    except Exception as e:
        print("error deleting user ({}) folder".format(chat_id), e)
        return False
    return True


def clear_scanned_and_temp(chat_id):
    delete_folder_for_user(chat_id, 'scanned')
    delete_folder_for_user(chat_id, 'temp')


def clear_cropped(chat_id):
    delete_folder_for_user(chat_id, 'cropped')


def user_has_images(chat_id):
    if len(get_original_images(chat_id)):
        return True
    else:
        return False


def user_has_cropped_images(chat_id):
    if len(get_cropped_images(chat_id)):
        return True
    else:
        return False


def user_has_scanned_images(chat_id):
    if len(get_scanned_images(chat_id)):
        return True
    else:
        return False


def find_and_crop(chat_id):
    clear_cropped(chat_id)
    images = get_original_images(chat_id)
    status = True
    for image in images:
        image = cv2.imread(str(image))
        cropped, image = crop.find_document(image)
        if not cropped:
            status = False
        path = get_cropped_path(chat_id)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S%f")
        # write png
        filename = str(path) + '/' + timestamp + '.png'
        cv2.imwrite(filename, image)
        # write jpg
        filename = str(path.joinpath('jpg')) + '/' + timestamp + '.jpg'
        cv2.imwrite(filename, image)

    return status


def shrink_originals(chat_id):
    clear_scanned_and_temp(chat_id)
    save_forlder = str(get_scans_path(chat_id))
    images = [str(x) for x in get_original_images(chat_id)]
    if images:
        prepare_for_scanning(images, chat_id)
        images = [str(x) for x in get_temp_images(chat_id)]
        shrink(images, save_forlder)


def prepare_for_scanning(images, chat_id):
    path = get_temp_path(chat_id)
    for image in images:
        img = cv2.imread(image)
        img_adapt = img_as_float(img)
        hist_eql = exposure.equalize_adapthist(img_adapt, clip_limit=0.03)

        img = img_as_ubyte(denoise_wavelet(hist_eql, multichannel=True))
        filename = str(path) + "/{}".format(image.split('/')[-1])
        cv2.imwrite(filename, img)


def shrink_cropped(chat_id):
    clear_scanned_and_temp(chat_id)
    save_forlder = str(get_scans_path(chat_id))
    images = [str(x) for x in get_cropped_images(chat_id)]
    if images:
        prepare_for_scanning(images, chat_id)
        images = [str(x) for x in get_temp_images(chat_id)]
        shrink(images, save_forlder)


def shrink(filenames, save_forlder):
    options = argparse.Namespace(basename='page', filenames=filenames, global_palette=False, num_colors=8,
                                 pdf_cmd='convert %i %o', pdfname='out/output.pdf', postprocess_cmd=None,
                                 postprocess_ext='_post.png', quiet=False, sample_fraction=0.05, sat_threshold=0.2,
                                 saturate=True, sort_numerically=True, value_threshold=0.25,
                                 white_bg=True)
    notescan_main(options, save_forlder)

