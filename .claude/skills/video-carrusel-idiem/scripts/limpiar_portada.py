#!/usr/bin/env python3
"""Plan B para la foto de fondo: borra los textos de la lámina de portada (inpainting) cuando no está
la foto original. Siempre es preferible la foto original de la librería, recortada igual que la lámina.

Uso:
    python3 scripts/limpiar_portada.py lamina_portada.jpg foto_limpia.jpg \
        --rect 40,40,440,110 --rect 795,50,1035,155 --rect 40,750,950,805 --rect 40,900,830,1030

Cada --rect es x0,y0,x1,y1 en píxeles (lámina 1080×1080) de una zona con texto o logo.
Solo se borran los píxeles blancos y rojos (texto de marca) dentro de cada rectángulo.
Funciona bien sobre fondos desenfocados u oscuros; sobre detalle nítido deja manchas: revisa el resultado.
"""
import argparse

import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada"); ap.add_argument("salida")
    ap.add_argument("--rect", action="append", required=True)
    a = ap.parse_args()
    im = cv2.imread(a.entrada)
    if im is None:
        raise SystemExit(f"No pude abrir {a.entrada}")
    b, g, r = [im[..., i].astype(np.int32) for i in range(3)]
    white = np.minimum(np.minimum(r, g), b) > 170
    red = (r > 150) & (g < 110) & (b < 110) & (r - g > 80)
    mask = np.zeros(im.shape[:2], np.uint8)
    for s in a.rect:
        x0, y0, x1, y1 = [int(v) for v in s.split(",")]
        mask[y0:y1, x0:x1] = ((white | red)[y0:y1, x0:x1]).astype(np.uint8) * 255
    mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    outp = cv2.inpaint(im, mask, 9, cv2.INPAINT_TELEA)
    blur = cv2.GaussianBlur(outp, (0, 0), 6)
    soft = cv2.GaussianBlur(mask, (0, 0), 4).astype(np.float32)[..., None] / 255.0
    outp = (outp * (1 - soft) + blur * soft).astype(np.uint8)
    cv2.imwrite(a.salida, outp, [cv2.IMWRITE_JPEG_QUALITY, 93])
    print(f"OK  {a.salida}  ({int((mask > 0).sum())} px reconstruidos) — revísala a ojo antes de usarla")


if __name__ == "__main__":
    main()
