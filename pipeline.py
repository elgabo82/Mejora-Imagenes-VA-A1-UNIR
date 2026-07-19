"""
Pipeline de mejora de imagen — Actividad 1, Visión Artificial (MUIA-UNIR)
Funciones de ajuste de intensidad, procesamiento de histograma y operadores
aritméticos, más métricas de evaluación sin referencia.
"""
import numpy as np
import cv2
from skimage.measure import shannon_entropy


# ---------------------------------------------------------------------------
# 1) Funciones de ajuste de intensidad (operan sobre la imagen RGB completa)
# ---------------------------------------------------------------------------
def negative(img):
    return 255 - img


def log_transform(img):
    img_f = img.astype(np.float64)
    c = 255.0 / np.log(1 + img_f.max())
    return np.clip(c * np.log(1 + img_f), 0, 255).astype(np.uint8)


def gamma_transform(img, gamma=0.4):
    img_f = img.astype(np.float64) / 255.0
    return np.clip(np.power(img_f, gamma) * 255, 0, 255).astype(np.uint8)


def percentile_contrast_stretch(img, low_pct=2, high_pct=98):
    lo, hi = np.percentile(img, (low_pct, high_pct))
    if hi <= lo:
        return img.copy()
    out = (img.astype(np.float64) - lo) * (255.0 / (hi - lo))
    return np.clip(out, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# 2) Procesamiento de histograma (sobre el canal de luminancia Y de YCrCb,
#    para no distorsionar el color al ecualizar canal por canal)
# ---------------------------------------------------------------------------
def histogram_equalization_color(img_rgb):
    ycrcb = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y_eq = cv2.equalizeHist(y)
    out = cv2.merge([y_eq, cr, cb])
    return cv2.cvtColor(out, cv2.COLOR_YCrCb2RGB)


def clahe_color(img_rgb, clip_limit=2.0, tile_grid_size=(8, 8)):
    ycrcb = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    y_eq = clahe.apply(y)
    out = cv2.merge([y_eq, cr, cb])
    return cv2.cvtColor(out, cv2.COLOR_YCrCb2RGB)


# ---------------------------------------------------------------------------
# 3) Operadores aritméticos
# ---------------------------------------------------------------------------
def linear_adjust(img, alpha=1.3, beta=25):
    out = img.astype(np.float64) * alpha + beta
    return np.clip(out, 0, 255).astype(np.uint8)


def unsharp_mask(img_rgb, sigma=3, amount=1.5):
    img_f = img_rgb.astype(np.float64)
    blurred = cv2.GaussianBlur(img_f, (0, 0), sigmaX=sigma)
    mask = img_f - blurred                       # resta -> aísla el detalle fino
    sharpened = img_f + amount * mask             # suma -> refuerza ese detalle
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def illumination_correction_division(img_gray, sigma=31, gain=128):
    img_f = img_gray.astype(np.float64) + 1e-6
    illumination = cv2.GaussianBlur(img_f, (0, 0), sigmaX=sigma)
    corrected = gain * (img_f / illumination)      # división -> corrige iluminación desigual
    return np.clip(corrected, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Métricas sin referencia
# ---------------------------------------------------------------------------
def to_gray(img_rgb):
    if img_rgb.ndim == 2:
        return img_rgb
    return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)


def compute_metrics(img_rgb):
    gray = to_gray(img_rgb).astype(np.float64)
    return {
        "brillo_medio": round(float(gray.mean()), 2),
        "contraste_rms": round(float(gray.std()), 2),
        "entropia": round(float(shannon_entropy(gray.astype(np.uint8))), 2),
    }
