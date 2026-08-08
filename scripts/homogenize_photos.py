"""Homogenize product photo scale: crop to content bbox, remove near-uniform
background (e.g. divisa's grey studio backdrop), and recompose on a pure white
canvas so every item fills the frame the same way the Polo photo does."""
from PIL import Image
import numpy as np
from scipy import ndimage
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LARGE_DIR = os.path.join(ROOT, 'assets', 'merch', 'large')
THUMB_DIR = os.path.join(ROOT, 'assets', 'merch')

SLUGS = [
    'tshirt-allenamento-gialla', 'tshirt-prepartita-nera', 'felpa-nera',
    'polo-rappresentanza', 'giacca-softshell', 'pantaloni-lunghi',
    'pantaloncini-corti', 'pantaloncini-allenamento', 'borsone-adrenalina',
    'zaino-tracolla', 'pochette', 'braccialetto-corda',
    'berretto-visiera-curva', 'berretto-invernale', 'berretto-visiera-piatta',
    'cuscino-gradinate', 'scaldacollo-pile', 'divisa-gara',
]


def neutralize_background(arr, tol=18):
    """Sample the border's dominant color and flatten near-matches to white."""
    h, w, _ = arr.shape
    border = np.concatenate([
        arr[0:8, :].reshape(-1, 3), arr[-8:, :].reshape(-1, 3),
        arr[:, 0:8].reshape(-1, 3), arr[:, -8:].reshape(-1, 3),
    ])
    colors, counts = np.unique(border.reshape(-1, 3), axis=0, return_counts=True)
    bg = colors[np.argmax(counts)].astype(int)
    dist = np.abs(arr.astype(int) - bg).sum(axis=2)
    mask = dist <= tol
    out = arr.copy()
    out[mask] = [255, 255, 255]
    return out, bg


def content_bbox(arr, thresh=30):
    """Union bbox of all sizeable connected non-white blobs (so a two-part
    photo like front+back jersey keeps both halves), dropping tiny specks
    that are just JPEG noise."""
    dist = np.abs(arr.astype(int) - 255).sum(axis=2)
    mask = dist > thresh
    # dilate slightly first so a logo/print detached from the garment outline
    # by anti-aliased white still merges into the same blob as the garment
    mask = ndimage.binary_dilation(mask, iterations=3)
    labeled, n = ndimage.label(mask)
    if n == 0:
        return 0, 0, arr.shape[1], arr.shape[0]
    objs = ndimage.find_objects(labeled)
    sizes = ndimage.sum(mask, labeled, range(1, n + 1))
    densities = []
    for i, sl in enumerate(objs):
        bbox_area = (sl[0].stop - sl[0].start) * (sl[1].stop - sl[1].start)
        densities.append(sizes[i] / bbox_area if bbox_area else 0)
    densities = np.array(densities)
    # thin decorative border/rule artifacts can be as large in pixel-count as
    # the real product but are sparse (low fill density) relative to their own
    # bounding box, so require both a reasonable size AND a solid fill
    keep = [i + 1 for i, (s, d) in enumerate(zip(sizes, densities))
            if s >= 0.25 * sizes.max() and d >= 0.2]
    if not keep:
        keep = [int(np.argmax(sizes)) + 1]
    ys, xs = np.where(np.isin(labeled, keep))
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def maybe_flatten_secondary_background(arr, x0, y0, x1, y1, tol=70):
    """Some source photos (e.g. divisa) sit on a light grey studio backdrop
    that doesn't touch the image border, so the border sampler misses it.
    Sample a frame around the bbox perimeter (not just 4 corner patches,
    which can land on the product itself for irregular/multi-part shapes)
    and flatten that color too if it looks like a background, not the item."""
    band = 8
    strips = [
        arr[y0:y0 + band, x0:x1], arr[y1 - band:y1, x0:x1],
        arr[y0:y1, x0:x0 + band], arr[y0:y1, x1 - band:x1],
    ]
    pixels = np.concatenate([s.reshape(-1, 3) for s in strips])
    # quantize before voting so JPEG noise doesn't fragment one background
    # shade into many near-identical buckets that each lose to solid white
    quantized = (pixels.astype(int) // 8) * 8
    colors, counts = np.unique(quantized, axis=0, return_counts=True)
    candidate = colors[np.argmax(counts)].astype(int) + 4
    r, g, b = candidate
    is_greyish = max(abs(r - g), abs(g - b), abs(r - b)) < 12
    is_light = candidate.mean() > 130
    is_not_already_white = candidate.mean() < 248
    if not (is_greyish and is_light and is_not_already_white):
        return arr, False
    dist = np.abs(arr.astype(int) - candidate).sum(axis=2)
    out = arr.copy()
    out[dist <= tol] = [255, 255, 255]
    return out, True


def process(slug, target_fill, size, out_dir):
    im = Image.open(os.path.join(LARGE_DIR, f'{slug}.jpg')).convert('RGB')
    arr = np.array(im)
    arr, bg = neutralize_background(arr)
    x0, y0, x1, y1 = content_bbox(arr)
    arr, flattened = maybe_flatten_secondary_background(arr, x0, y0, x1, y1)
    if flattened:
        x0, y0, x1, y1 = content_bbox(arr)
    pad = 3
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(arr.shape[1], x1 + pad), min(arr.shape[0], y1 + pad)
    crop = Image.fromarray(arr).crop((x0, y0, x1, y1))

    max_dim = max(crop.width, crop.height)
    target_px = target_fill * size
    scale = target_px / max_dim
    new_w, new_h = max(1, round(crop.width * scale)), max(1, round(crop.height * scale))
    resized = crop.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new('RGB', (size, size), (255, 255, 255))
    x = (size - new_w) // 2
    y = (size - new_h) // 2
    canvas.paste(resized, (x, y))
    canvas.save(os.path.join(out_dir, f'{slug}.jpg'), 'JPEG', quality=88)
    return (x1 - x0), (y1 - y0), bg


if __name__ == '__main__':
    # calibrate target fill ratio from the polo reference photo
    ref = np.array(Image.open(os.path.join(LARGE_DIR, 'polo-rappresentanza.jpg')).convert('RGB'))
    ref, _ = neutralize_background(ref)
    x0, y0, x1, y1 = content_bbox(ref)
    ref_max_dim = max(x1 - x0, y1 - y0)
    TARGET_FILL = ref_max_dim / ref.shape[0]
    print(f'Polo content bbox: {x1-x0}x{y1-y0} of {ref.shape[0]} -> target fill {TARGET_FILL:.3f}')

    import sys
    preview = '--apply' not in sys.argv
    large_out = os.path.join(ROOT, 'scratch_preview', 'large') if preview else LARGE_DIR
    thumb_out = os.path.join(ROOT, 'scratch_preview', 'thumb') if preview else THUMB_DIR
    os.makedirs(large_out, exist_ok=True)
    os.makedirs(thumb_out, exist_ok=True)

    for slug in SLUGS:
        w, h, bg = process(slug, TARGET_FILL, 700, large_out)
        process(slug, TARGET_FILL, 200, thumb_out)
        print(f'{slug:28s} bbox {w:4d}x{h:<4d} bg={tuple(bg)}')
    print('PREVIEW mode' if preview else 'APPLIED to assets/merch')
