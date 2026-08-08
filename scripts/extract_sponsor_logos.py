"""Crop the sponsor grid images into individual transparent-background PNGs
for the scrolling sponsor ticker."""
from PIL import Image
import numpy as np
from scipy import ndimage
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(ROOT, 'Input')
OUT_DIR = os.path.join(ROOT, 'assets', 'sponsors')
os.makedirs(OUT_DIR, exist_ok=True)

TARGET_H = 220  # render height before final CSS scale-down, keeps logos crisp


def save_transparent(crop_rgba, out_path):
    # trim to content's own tight bbox once more (padding creeps in from dilation)
    alpha = np.array(crop_rgba)[:, :, 3]
    ys, xs = np.where(alpha > 10)
    pad = 6
    x0, y0 = max(0, xs.min() - pad), max(0, ys.min() - pad)
    x1, y1 = min(crop_rgba.width, xs.max() + pad), min(crop_rgba.height, ys.max() + pad)
    crop_rgba = crop_rgba.crop((x0, y0, x1, y1))

    scale = TARGET_H / crop_rgba.height
    new_size = (max(1, round(crop_rgba.width * scale)), TARGET_H)
    crop_rgba = crop_rgba.resize(new_size, Image.LANCZOS)
    crop_rgba.save(out_path, 'PNG')
    print(f'{os.path.basename(out_path):32s} {crop_rgba.width}x{crop_rgba.height}')


def extract_from_dark_grid(src_path, anchors, dilate_iter=35, mask_thresh=20):
    """anchors: {slug: (x_center, y_center)} approximate position of each logo
    in the source image -- each detected blob is matched to its nearest anchor,
    which is far more robust than guessing a reading-order sort on an
    irregular grid. Bump mask_thresh if the source has a faint decorative
    background pattern (not pure black) that would otherwise register as
    its own tiny stray blobs."""
    im = Image.open(src_path).convert('RGB')
    arr = np.array(im)
    mask = arr.mean(axis=2) > mask_thresh
    dilated = ndimage.binary_dilation(mask, iterations=dilate_iter)
    labeled, n = ndimage.label(dilated)
    objs = ndimage.find_objects(labeled)

    rgba_arr = np.array(Image.fromarray(arr).convert('RGBA'))
    rgba_arr[:, :, 3] = np.where(mask, 255, 0)

    assert n == len(anchors), f'{n} blobs found, expected {len(anchors)}'
    for i, sl in enumerate(objs):
        label = i + 1
        cy = (sl[0].start + sl[0].stop) / 2
        cx = (sl[1].start + sl[1].stop) / 2
        slug = min(anchors, key=lambda s: (anchors[s][0] - cx) ** 2 + (anchors[s][1] - cy) ** 2)
        sub_mask = mask[sl] & (labeled[sl] == label)
        ys, xs = np.where(sub_mask)
        cx0, cy0 = sl[1].start + xs.min(), sl[0].start + ys.min()
        cx1, cy1 = sl[1].start + xs.max() + 1, sl[0].start + ys.max() + 1
        crop = Image.fromarray(rgba_arr[cy0:cy1, cx0:cx1])
        save_transparent(crop, os.path.join(OUT_DIR, f'{slug}.png'))


def extract_from_white_bg(src_path, slug, dark_to_white=False, dark_thresh=120):
    """dark_to_white: some logos were designed for print on white and use
    black text/outlines that vanish against the dark ticker background --
    recolor those to white. Uses max-channel (not mean) so it never touches
    saturated brand colors (a vivid green/blue still has a high channel even
    if it reads 'dark' on average)."""
    im = Image.open(src_path).convert('RGB')
    arr = np.array(im).astype(int)
    mask = arr.mean(axis=2) < 245  # content = not white (this is the alpha mask)
    if dark_to_white:
        near_black = arr.max(axis=2) < dark_thresh
        arr[near_black] = [255, 255, 255]
    rgba_arr = np.dstack([arr, np.where(mask, 255, 0)]).astype('uint8')
    crop = Image.fromarray(rgba_arr)
    save_transparent(crop, os.path.join(OUT_DIR, f'{slug}.png'))


if __name__ == '__main__':
    extract_from_dark_grid(
        os.path.join(INPUT_DIR, 'sponsor schiena.png'),
        {
            'motonautica-zattoni': (2136, 220),
            'flows-comunicazione': (418, 227),
            'arianuova-immobiliare': (1277, 631),
            'claudio-marongiu': (378, 743),
            'npm': (2157, 763),
            'le-mura-sport-village': (1796, 1501),
            'fassa-village': (705, 1503),
        },
    )
    extract_from_dark_grid(
        os.path.join(INPUT_DIR, 'sponsor fronte.png'),
        {
            'arredo-uno': (878, 424),
            'polycykle': (902, 1240),
        },
        mask_thresh=40,
    )
    extract_from_white_bg(os.path.join(INPUT_DIR, 'Yakata Sport.png'), 'yakata-sport')
