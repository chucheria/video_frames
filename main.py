import cv2
from os import path, listdir
from PIL import Image


def calc_skip_frames(video, n_img):
    """ Calculate number of frames to skip based on the number of images
    to extract from the video

    :param video: OpenCV video capture
    :param n_img: number of images to extract
    :return: int
    """
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/fps
    return int(fps * duration / n_img)


def get_frames(video_path, images_folder, n_img=20, resize=0):
    cap = cv2.VideoCapture(video_path)

    frame_skip = calc_skip_frames(cap, n_img)

    i = 0
    img = 0
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break
        if i > frame_skip - 1:
            if 0 < resize < 1:
                width = int(frame.shape[1] * resize)
                height = frame.shape[0]
                dim = (width, height)
                frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

            cv2.imwrite(path.join(images_folder, f'img_{str(img)}.png'), frame)
            i = 0
            img += 1
            continue
        i += 1

    cap.release()
    cv2.destroyAllWindows()


def get_concat_h_multi_resize(im_list, resample=Image.BICUBIC):
    min_height = min(im.height for im in im_list)
    im_list_resize = [im.resize((int(im.width * min_height / im.height), min_height), resample=resample)
                      for im in im_list]
    total_width = sum(im.width for im in im_list_resize)
    dst = Image.new('RGB', (total_width, min_height))
    pos_x = 0
    for im in im_list_resize:
        dst.paste(im, (pos_x, 0))
        pos_x += im.width
    return dst


def array_images(folder_img):
    array_img = []
    files = [file for file in listdir(folder_img) if file.endswith('png')]
    for img_file in files:
        img = Image.open(path.join(folder_img, img_file))
        array_img.append(img)

    return array_img


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # A0: 841x1189 mm
    # A1: 594x841 mm
    # A2: 420x594 mm
    # A3: 297x420 mm
    # A4: 210x297 mm
    # A5: 148x210 mm
    # A6: 105x148 mm -> 300 dpi  1 240 x 1 748 px

    n_img = 25

    video_p = path.join('data', 'video', 'A.Monster.Calls.2016.720p.BluRay.x264-[YTS.AG].mp4')
    images_f = path.join('data', 'image')
    get_frames(video_p, images_f, n_img)
    imgs = array_images(images_f)
    get_concat_h_multi_resize(imgs).resize((1748, 1240), Image.ANTIALIAS).save(path.join(images_f, 'stack.png'), dpi=(300,300))
