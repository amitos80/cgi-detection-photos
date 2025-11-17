#!/usr/bin/env python3
"""
Demo runner for RAMBiNo-inspired feature extractor.
Generates two synthetic images (real-like and cgi-like), computes features,
and prints a short report. Use this to tune parameters quickly.
"""
import io
import numpy as np
from PIL import Image
from forensics import rambino, engine


def make_real_like(size=256):
    # gradient + high-frequency sensor-like noise
    x = np.linspace(0, 1, size, dtype=np.float32)
    grad = np.tile(x, (size, 1))
    # add per-pixel Gaussian noise mimicking sensor noise
    noise = np.random.normal(loc=0.0, scale=0.02, size=(size, size)).astype(np.float32)
    img = grad + noise
    img = np.clip(img, 0.0, 1.0)
    arr = (img * 255).astype(np.uint8)
    return arr


def make_cgi_like(size=256):
    # smooth bands + small synthetic texture (low-frequency)
    img = np.zeros((size, size), dtype=np.float32)
    # add few circular blobs
    cx, cy = size // 2, size // 2
    Y, X = np.ogrid[:size, :size]
    r = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    img += np.clip(1.0 - (r / (size * 0.6)), 0.0, 1.0)
    # add mild low-frequency noise
    lf_noise = np.random.normal(scale=0.005, size=(size, size)).astype(np.float32)
    img = img + lf_noise
    img = np.clip(img, 0.0, 1.0)
    arr = (img * 255).astype(np.uint8)
    return arr


def arr_to_jpeg_bytes(arr, quality=95):
    im = Image.fromarray(arr)
    buf = io.BytesIO()
    im.save(buf, format='JPEG', quality=quality)
    return buf.getvalue()


def report_features(name, arr):
    feats = rambino.compute_rambino_features(arr, wavelet='db2', level=2, bins=32)
    print(f"--- {name} ---")
    print(f"feature length: {feats.size}")
    print(f"mean: {feats.mean():.6f}, std: {feats.std():.6f}")
    print(f"first 12 features: {feats.flatten()[:12].tolist()}")
    # run through engine (bytes)
    b = arr_to_jpeg_bytes(arr)
    res = engine.run_analysis(b)
    print(f"engine prediction: {res['prediction']}, confidence: {res['confidence']:.4f}")
    print()


def main():
    np.random.seed(0)
    real = make_real_like(256)
    cgi = make_cgi_like(256)

    report_features('Real-like synthetic', real)
    report_features('CGI-like synthetic', cgi)

if __name__ == '__main__':
    main()

