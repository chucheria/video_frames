import argparse
from os import path, listdir, remove

import cv2
from PIL import Image

parser = argparse.ArgumentParser(description='Choose size of paper to print')
parser.add_argument("--paper", dest='paper_size', type=str, default='a6',
                    choices=['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6'])
parser.add_argument("-n", dest='n_img', type=int, default=2000)
parser.add_argument("-v", dest='video_p', type=str)
parser.add_argument("-i", dest='images_f', type=str)


def calc_skip_frames(video, n_img):
    """ Calculate number of frames to skip based on the number of images
    to extract from the video

    :param video: OpenCV video capture
    :param n_img: int number of images to extract
    :return: int number of frames to skip
    """
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    return int(fps * duration / n_img)


def get_frames(video_path, images_folder, extension='png', n_img=2000):
    """ Get n_img number of frames of a video

    :param video_path: string path of video
    :param images_folder: string path to save images
    :param extension: string extension for saving images
    :param n_img: int number of frames to extract
    :return: bool true
    """
    cap = cv2.VideoCapture(video_path)

    frame_skip = calc_skip_frames(cap, n_img)

    i = 0
    img = 0 # Number of image to save
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if i > frame_skip - 1:
            cv2.imwrite(path.join(images_folder, f'img_{str(img)}.{extension}'), frame)
            i = 0
            img += 1
            continue
        i += 1

    cap.release()
    cv2.destroyAllWindows()

    return True


def concat_h_resize(img_list, resample=Image.BICUBIC):
    """ Horizontal concatenation of a list of PIL images

    :param img_list: list of PIL images to concatenate
    :param resample: resample option to resize, use BICUBIC for speed,
                     ANTIALIAS for quality
    :return: PIL image
    """
    min_height = min(im.height for im in img_list)
    im_resize = [im.resize(
        (int(im.width * min_height / im.height), min_height), resample=resample)
                      for im in img_list]
    total_width = sum(im.width for im in im_resize)
    dst = Image.new('RGB', (total_width, min_height))
    pos_x = 0
    for im in im_resize:
        dst.paste(im, (pos_x, 0))
        pos_x += im.width

    return dst


def array_images(folder_img, extension='png', remove_src_img=False):
    """ Read images and save PIL images to an array

    :param folder_img: string folder with images
    :param extension: string with extension file for images
    :param remove_src_img: bool if true remove original images which create new image
    :return:
    """

    array_img = []
    files = [file for file in listdir(folder_img) if file.endswith(extension)]
    for img_file in files:
        img = Image.open(path.join(folder_img, img_file))
        array_img.append(img)
        if remove_src_img:
            remove(img_file)

    return array_img


def mm_to_pix(mm, dpi=300):
    """

    :param mm: float mm to convert to pix
    :param dpi: int dpi
    :return: int pixels
    """
    return int(mm * dpi / 25.4)


if __name__ == '__main__':

    args = parser.parse_args()

    if args.paper_size == 'a0':
        resize_px_w = mm_to_pix(1189)
        resize_px_h = mm_to_pix(841)
    elif args.paper_size == 'a1':
        resize_px_w = mm_to_pix(841)
        resize_px_h = mm_to_pix(594)
    elif args.paper_size == 'a2':
        resize_px_w = mm_to_pix(594)
        resize_px_h = mm_to_pix(420)
    elif args.paper_size == 'a3':
        resize_px_w = mm_to_pix(420)
        resize_px_h = mm_to_pix(297)
    elif args.paper_size == 'a4':
        resize_px_w = mm_to_pix(297)
        resize_px_h = mm_to_pix(210)
    elif args.paper_size == 'a5':
        resize_px_w = mm_to_pix(210)
        resize_px_h = mm_to_pix(148)
    else:
        resize_px_w = mm_to_pix(148)
        resize_px_h = mm_to_pix(105)

    get_frames(args.video_p, args.images_f, args.n_img)
    imgs = array_images(args.images_f)
    concat_h_resize(imgs)\
        .resize((resize_px_w, resize_px_h), Image.ANTIALIAS)\
        .save(path.join(args.images_f, 'stack.png'), dpi=(300,300))
