# deband.py (fast version, 24 Oct 2026): band-free export for every smooth area of a slide.
# Smoothing blurs run at half resolution with OpenCV (a smooth ramp loses nothing), flat and tiny
# regions are skipped, and video frames that repeat are processed once.
import sys, os, hashlib, numpy as np, cv2
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_dilation, label, find_objects

def downscale_float(img, size=(1080, 1350)):
    chans = [np.asarray(c.resize(size, Image.LANCZOS), dtype=np.float64)
             for c in (ch.convert('F') for ch in img.convert('RGB').split())]
    return np.stack(chans, axis=2)

_grain_cache = {}
def _grain(shape, grain, broad, seed):
    key = (shape, grain, broad, seed)
    if key not in _grain_cache:
        rng = np.random.default_rng(seed)
        nz = rng.random(shape) - rng.random(shape)
        nz = gaussian_filter(nz, 0.6); nz = nz / nz.std() * (grain / 2.45)
        lf = gaussian_filter(rng.standard_normal(shape), 3.0); lf = lf / lf.std() * broad
        _grain_cache[key] = nz + lf
    return _grain_cache[key]

def deband(a, sigma=14, tol=3.0, grain=1.2, broad=0.30, seed=7):
    lum = a.mean(axis=2)
    gy, gx = np.gradient(gaussian_filter(lum, 0.7))
    edge = binary_dilation(np.hypot(gx, gy) > 2.0, iterations=3)
    smooth = ~edge
    lab, n = label(smooth)
    out = a.copy()
    pad = int(3 * sigma) + 2
    for i, sl in enumerate(find_objects(lab), start=1):
        if sl is None: continue
        y0 = max(sl[0].start - pad, 0); y1 = min(sl[0].stop + pad, a.shape[0])
        x0 = max(sl[1].start - pad, 0); x1 = min(sl[1].stop + pad, a.shape[1])
        reg = lab[y0:y1, x0:x1] == i
        if reg.sum() < 400: continue                       # too small to show a band
        src = a[y0:y1, x0:x1]
        vals = src[reg]
        if (vals.max(0) - vals.min(0)).max() <= 1.0: continue   # flat fill: nothing to smooth
        m = reg.astype(np.float32)
        h, w = reg.shape; hh, hw = max(h // 2, 1), max(w // 2, 1)
        num = cv2.resize((src * m[..., None]).astype(np.float32), (hw, hh), interpolation=cv2.INTER_AREA)
        den = cv2.resize(m, (hw, hh), interpolation=cv2.INTER_AREA)
        k = int(4 * sigma / 2) * 2 + 1
        num = cv2.GaussianBlur(num, (k, k), sigma / 2, borderType=cv2.BORDER_REPLICATE)
        den = cv2.GaussianBlur(den, (k, k), sigma / 2, borderType=cv2.BORDER_REPLICATE)
        num = cv2.resize(num, (w, h), interpolation=cv2.INTER_LINEAR)
        den = cv2.resize(den, (w, h), interpolation=cv2.INTER_LINEAR)
        sm = num.astype(np.float64) / np.maximum(den, 1e-6)[..., None]
        ok = reg[..., None] & (np.abs(sm - src) <= tol)
        out[y0:y1, x0:x1] = np.where(ok, sm, out[y0:y1, x0:x1])
    soft_mask = gaussian_filter(smooth.astype(np.float64), 1.0)
    out = out + (_grain(lum.shape, grain, broad, seed) * soft_mask)[..., None]
    return np.clip(np.round(out), 0, 255).astype(np.uint8), smooth.mean()

def deband_frames(src_dir, dst_dir, k=0, n=1, grain=0.8, broad=0.0):
    """Video: process worker k of n; frames identical to an earlier one reuse its result."""
    os.makedirs(dst_dir, exist_ok=True)
    fs = sorted(f for f in os.listdir(src_dir) if f.endswith('.png'))
    hashes = [hashlib.md5(open(os.path.join(src_dir, f), 'rb').read()).hexdigest() for f in fs]
    first = {}
    for f, h in zip(fs, hashes): first.setdefault(h, f)
    uniq = sorted(set(first.values()))
    for f in uniq[k::n]:
        im = Image.open(os.path.join(src_dir, f))
        a = downscale_float(im) if im.size != (1080, 1350) else np.asarray(im.convert('RGB'), dtype=np.float64)
        Image.fromarray(deband(a, grain=grain, broad=broad)[0]).save(os.path.join(dst_dir, f), compress_level=1)
    return fs, hashes, first

def link_duplicates(src_dir, dst_dir):
    """Run once after all workers finish: copy each repeated frame from its first occurrence."""
    import shutil
    fs = sorted(f for f in os.listdir(src_dir) if f.endswith('.png'))
    first = {}
    for f in fs:
        h = hashlib.md5(open(os.path.join(src_dir, f), 'rb').read()).hexdigest()
        if h in first: shutil.copyfile(os.path.join(dst_dir, first[h]), os.path.join(dst_dir, f))
        else: first[h] = f

if __name__ == '__main__':
    if sys.argv[1] == 'frames':        # deband.py frames SRC DST K N
        deband_frames(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    elif sys.argv[1] == 'link':        # deband.py link SRC DST
        link_duplicates(sys.argv[2], sys.argv[3])
    else:                              # deband.py IN OUT   (still slide)
        im = Image.open(sys.argv[1])
        a = downscale_float(im) if im.size != (1080, 1350) else np.asarray(im.convert('RGB'), dtype=np.float64)
        o, f = deband(a); Image.fromarray(o).save(sys.argv[2]); print(sys.argv[2], 'smooth fraction', round(f, 3))
