"""Build homogenized product photos straight from the original source images
(catalog PDF extractions + Input/ photos), not from already-cropped output --
chaining crops on top of crops compounds measurement error. Every item ends
up filling its white canvas the same way the Polo reference photo does, with
any studio backdrop flattened to pure white."""
from PIL import Image
import numpy as np
from scipy import ndimage
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_DIR = os.path.join(ROOT, 'scratch_catalog')
INPUT_DIR = os.path.join(ROOT, 'Input')
LARGE_DIR = os.path.join(ROOT, 'assets', 'merch', 'large')
THUMB_DIR = os.path.join(ROOT, 'assets', 'merch')

# slug -> source file (relative to CATALOG_DIR unless it's an absolute-ish Input path)
SOURCES = {
    'tshirt-allenamento-gialla': ('catalog', 'p3_img4_1090x1158.png'),
    'tshirt-prepartita-nera': ('catalog', 'p4_img5_1383x1364.png'),
    'felpa-nera': ('catalog', 'p5_img5_1200x1200.png'),
    'polo-rappresentanza': ('catalog', 'p6_img4_600x806.png'),
    'giacca-softshell': ('catalog', 'p7_img3_618x818.png'),
    'pantaloni-lunghi': ('catalog', 'p8_img3_598x749.png'),
    'pantaloncini-corti': ('catalog', 'p9_img3_806x1107.png'),
    'borsone-adrenalina': ('catalog', 'p10_img1_602x753.png'),
    'zaino-tracolla': ('catalog', 'p10_img2_782x785.png'),
    'pochette': ('catalog', 'p11_img1_873x722.png'),
    'braccialetto-corda': ('catalog', 'p11_img3_1106x640.jpeg'),
    'berretto-visiera-curva': ('catalog', 'p12_img4_800x960.jpeg'),
    'berretto-invernale': ('catalog', 'p12_img1_904x720.jpeg'),
    'berretto-visiera-piatta': ('catalog', 'p13_img1_1332x1060.png'),
    'cuscino-gradinate': ('catalog', 'p13_img3_724x543.png'),
    'scaldacollo-pile': ('catalog', 'p14_img2_724x543.png'),
    'divisa-gara': ('input', 'divisa.jpeg'),
    'pantaloncini-allenamento': ('input', 'Pantaloncini corti allenamento..png'),
}

SLUGS = list(SOURCES.keys())


def source_path(slug):
    kind, fname = SOURCES[slug]
    base = CATALOG_DIR if kind == 'catalog' else INPUT_DIR
    return os.path.join(base, fname)


def neutralize_background(arr):
    """Flatten the studio backdrop to pure white, gradient/vignette and all.

    Some source photos aren't shot on white but on a light grey seamless
    backdrop that fades a bit toward the corners, so no single sampled color
    matches all of it. Instead: mark every pixel that is both grey (R~G~B)
    and light (not the dark garment) as background-*candidate*, then keep
    only the parts of that candidate mask connected to the image border --
    a flood fill from the edges. That follows the gradient correctly and
    stops at the object's outline, since the object is either dark or
    saturated in color and fails the grey+light test.
    """
    r = arr[:, :, 0].astype(int)
    g = arr[:, :, 1].astype(int)
    b = arr[:, :, 2].astype(int)
    greyish = (np.abs(r - g) < 15) & (np.abs(g - b) < 15) & (np.abs(r - b) < 15)
    light = arr.mean(axis=2) > 140
    candidate = greyish & light

    labeled, n = ndimage.label(candidate)
    border_labels = set(labeled[0, :]) | set(labeled[-1, :]) | set(labeled[:, 0]) | set(labeled[:, -1])
    border_labels.discard(0)
    bg_mask = np.isin(labeled, list(border_labels))

    out = arr.copy()
    out[bg_mask] = [255, 255, 255]
    bg_color = arr[bg_mask].mean(axis=0).astype(int) if bg_mask.any() else np.array([255, 255, 255])
    return out, bg_color


def content_bbox(arr, thresh=30):
    """Union bbox of all sizeable, reasonably solid connected non-white blobs
    (so a two-part photo like front+back jersey keeps both halves), dropping
    thin decorative-line artifacts and JPEG noise specks."""
    dist = np.abs(arr.astype(int) - 255).sum(axis=2)
    mask = dist > thresh
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
    keep = [i + 1 for i, (s, d) in enumerate(zip(sizes, densities))
            if s >= 0.25 * sizes.max() and d >= 0.2]
    if not keep:
        keep = [int(np.argmax(sizes)) + 1]
    ys, xs = np.where(np.isin(labeled, keep))
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def measure(slug):
    im = Image.open(source_path(slug)).convert('RGB')
    arr = np.array(im)
    arr, bg = neutralize_background(arr)
    x0, y0, x1, y1 = content_bbox(arr)
    return arr, (x0, y0, x1, y1), bg


def render(arr, bbox, target_fill, size, out_path):
    x0, y0, x1, y1 = bbox
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
    canvas.save(out_path, 'JPEG', quality=88)


if __name__ == '__main__':
    import sys
    preview = '--apply' not in sys.argv
    large_out = os.path.join(ROOT, 'scratch_preview', 'large') if preview else LARGE_DIR
    thumb_out = os.path.join(ROOT, 'scratch_preview', 'thumb') if preview else THUMB_DIR
    os.makedirs(large_out, exist_ok=True)
    os.makedirs(thumb_out, exist_ok=True)

    ref_arr, ref_bbox, _ = measure('polo-rappresentanza')
    rx0, ry0, rx1, ry1 = ref_bbox
    TARGET_FILL = max(rx1 - rx0, ry1 - ry0) / ref_arr.shape[0]
    print(f'Polo content bbox: {rx1-rx0}x{ry1-ry0} of {ref_arr.shape[0]} -> target fill {TARGET_FILL:.3f}')

    for slug in SLUGS:
        arr, bbox, bg = measure(slug)
        x0, y0, x1, y1 = bbox
        render(arr, bbox, TARGET_FILL, 700, os.path.join(large_out, f'{slug}.jpg'))
        render(arr, bbox, TARGET_FILL, 200, os.path.join(thumb_out, f'{slug}.jpg'))
        print(f'{slug:28s} bbox {x1-x0:4d}x{y1-y0:<4d} bg={tuple(bg)}')
    print('PREVIEW mode' if preview else 'APPLIED to assets/merch')
