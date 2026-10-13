---
name: video-carrusel-idiem
description: Convierte un carrusel o post aprobado de IDIEM en un video 1080×1080 para LinkedIn (MP4, opcionalmente con música original chill house), con animación sobria de marca. Usar cuando se pida "animar", "hacer video", "pasar a video" o "versión en movimiento" de un carrusel, post o lámina de IDIEM.
---

# Video de carrusel IDIEM

Convierte una pieza **ya aprobada** (carrusel: portada + N láminas + cierre) en un video cuadrado para LinkedIn.
El método está probado: el carrusel SIM del 11 de noviembre se regenera con este paquete y sale idéntico al video aprobado por Marketing.

## 0. Regla principal: no improvisar el método

La calidad sale de **cómo** se fabrica el video, no del prompt. Usa siempre este pipeline:

```
config JSON  →  scripts/build.py  →  video.html (línea de tiempo determinística)
             →  scripts/music.py  →  music.wav (opcional)
             →  scripts/render.py →  cuadro a cuadro con Chromium headless → video.mp4 / video_musica.mp4
             →  scripts/qa.py     →  hojas de control + chequeo técnico
```

**Errores que arruinan el resultado y están prohibidos:**

| No hacer | Por qué falla | Hacer en su lugar |
|---|---|---|
| Grabar la pantalla en tiempo real, o usar animaciones/transiciones CSS y capturar mientras corren | Saltos, cuadros perdidos, velocidad irregular | `window.seek(t)` + captura cuadro a cuadro (`render.py`) |
| Animar las láminas como imágenes planas (zoom/deslizar el PNG) | El texto queda "horneado" y pixelado; se ve como un slideshow | Reconstruir en capas: foto limpia + textos reales en HTML + logo SVG |
| Generar el video con IA generativa (Sora, Veo, Kling, etc.) | Deforma textos, cifras y logo | Solo código; la IA generativa no toca piezas con texto o marca |
| Dejar que el navegador use una fuente de reemplazo | Sale en DejaVu/Arial en vez de Montserrat | Montserrat va incrustada; `render.py` aborta si no carga |
| Reescribir, resumir o "mejorar" los textos | La pieza ya fue aprobada por MKT | Textos literales de la lámina, con sus mismos saltos de línea |
| Animaciones con rebote, elásticas, giros, zoom brusco, glitch | Contradice "precisión técnica" de la marca | El lenguaje de movimiento de la sección 3 |

## 1. Insumos (pedirlos o buscarlos antes de empezar)

1. **Textos de cada lámina, literales**: eyebrow y título de portada; por lámina, título (con la palabra en caja roja) y párrafo; párrafo del cierre. Copia los **mismos saltos de línea** de la lámina original.
2. **Foto de fondo original** desde la librería (la que indica la traza del post, p. ej. `PHO-0042`), recortada a 1080×1080 con el mismo encuadre de la lámina.
   - Plan B si no está: `scripts/limpiar_portada.py` borra los textos de la portada por inpainting. Revisa el resultado a ojo (funciona bien sobre fondos desenfocados u oscuros, mal sobre detalle nítido).
3. **Las láminas originales** (PNG/JPG) para la comparación final.
4. **Ícono por lámina**: nombre de archivo en `assets/icons/` (estilo Lucide, trazo fino, sin relleno). Si falta uno, copiar el SVG desde lucide.dev a esa carpeta.

Assets de marca ya incluidos en `assets/`: logo blanco con "d" roja (`logo_idiem_blanco.svg`, vectorial oficial), eslogan "Elige bien.Elige idiem." con transparencia (`eslogan_alfa.png`, en su tipografía real), Montserrat 400/700.

## 2. Configuración (`config/<pieza>.json`)

Copia `config/ejemplo_sim.json` y reemplaza los contenidos. Convenciones:

- `cover.title`: `*palabra*` va en rojo. Salto de línea con `\n` (el título crece hacia arriba).
- `steps[].title`: lista de líneas; `[texto]` va en caja roja. Ej.: `["Inspecciones [en]", "[terreno]"]`.
- `steps[].body` y `closing.body`: lista de líneas, tal como en la lámina.
- `photo.focus`: punto hacia donde avanza el zoom lento (el sujeto principal), p. ej. `"62% 54%"`.
- `photo.glow` (opcional): `{x, y, r}` de una fuente de luz real en la foto (focos, pantallas) para una "respiración" sutil. Omitir si no hay una luz evidente.
- `timing` (opcional): si se omite, se calcula solo (ver sección 4).

## 3. Lenguaje de movimiento (ya implementado en la plantilla, no cambiarlo sin pedirlo)

Marca = precisión técnica, sobriedad. El movimiento revela la información; no decora.

- **Un solo plano de fondo continuo**: la misma foto en todo el video, con zoom lento lineal 1,00 → 1,10. Al pasar de la portada a las láminas entra un velo oscuro (0,62–0,73 de opacidad) para legibilidad.
- **Curvas**: entradas con expo-out (rápidas al inicio, suaves al llegar); salidas con cubic-in, cortas (0,35–0,4 s) y 0,6 s antes del corte.
- **Títulos**: cada palabra sube desde una máscara (como si emergiera de una línea), escalonadas 0,11–0,13 s. La caja roja se barre de izquierda a derecha y la palabra entra 0,14 s después.
- **Barra roja de acento**: crece de izquierda a derecha y en la salida se retira hacia la derecha.
- **Íconos**: se dibujan trazo a trazo; cada trazo permanece invisible hasta que empieza (evita puntos sueltos).
- **Párrafo**: línea a línea (opacidad + 16 px hacia arriba), escalonado 0,1 s.
- **Persistentes**: el logo y el número de lámina no salen entre láminas; el número cambia con un dígito que rueda.
- **Cierre**: panel gris oscuro con degradado → eslogan → barra que crece desde el centro → párrafo → logo (escala 0,94 → 1) → URL. El video **termina sobre el logo**, sin fundido a negro.

Paleta y tipografía según el design system IDIEM: rojo `#e1261d`, gris oscuro `#2f3030`, texto `#eff0ef`; Montserrat Bold para títulos y Regular para párrafos; márgenes laterales de 60 px.

## 4. Tiempos

- Portada 4 s · cada lámina entre 5,5 y 9 s · cierre ≈ 6 s.
- Duración de lámina automática: `1,6 s + palabras / 4,4` (≈ 260 palabras por minuto de lectura más la entrada), redondeada a 0,5 s e igual para todas las láminas (manda la más larga).
- Todo se redondea a múltiplos de 0,5 s y la duración total a múltiplos de 2 s: a 120 BPM **cada corte cae en un pulso** de la música.
- Si un video supera ~45 s, decirlo antes de renderizar: probablemente el carrusel tiene demasiado texto para video y conviene pedirle a MKT una versión condensada (no recortar textos por cuenta propia).

## 5. Música (solo si se pide)

`scripts/music.py` compone una pista original chill house a 120 BPM a partir de los tiempos del video: la portada lleva solo ambiente, el ritmo entra en la lámina 01, hay un barrido suave antes de cada corte y en el cierre el ritmo se retira y resuelve. Es síntesis propia (sin samples ni derechos de terceros), normalizada a −17 LUFS con picos ≤ −1 dBTP.

- El agente **no puede escuchar**: solo mide volumen y balance. Entregar siempre el MP4 sin audio y el MP4 con música, y decir explícitamente que la música requiere aprobación auditiva de una persona.
- Variar la pista con `--seed N` si se quiere otra textura con la misma estructura.
- Nunca descargar música de internet ni usar temas comerciales.

## 6. Control de calidad (obligatorio antes de entregar)

1. `render.py` aborta si Montserrat no cargó o si algún texto sale del margen o choca con otro: corregir el JSON (partir líneas largas igual que en la lámina), no achicar letras a mano.
2. `qa.py --originales <carpeta>` debe pasar todos los chequeos técnicos (1080×1080, H.264, 30 fps, duración, y audio −17 ±1 LUFS si hay música).
3. Mirar **las imágenes** `qa/hoja_transiciones.jpg` y `qa/comparacion.jpg` (abrirlas, no suponer) y confirmar:
   - textos idénticos a la lámina original, letra por letra;
   - nada cortado ni fuera del margen;
   - íconos sin puntos sueltos; sin cuadros vacíos de más de 0,3 s;
   - logo y número estables entre láminas; el último cuadro muestra el logo.
4. Si algo falla, corregir y volver a renderizar. No entregar con observaciones abiertas.

## 7. Entrega

- `video.mp4` (sin audio) y, si se pidió, `video_musica.mp4`.
- `video.html` (abre en el navegador; clic reinicia, espacio pausa) para revisar el movimiento sin descargar.
- Una nota breve con: duración, de dónde salió la foto (original o reconstruida), qué se agregó que no estaba en las láminas (zoom, luz, música) y cualquier diferencia con la pieza aprobada.

## Comandos

```bash
# una vez por máquina
pip install playwright numpy scipy pillow opencv-python-headless && python -m playwright install chromium
# ffmpeg debe estar instalado (brew install ffmpeg / apt install ffmpeg)

# por video (desde la carpeta de esta skill)
python3 scripts/build.py config/mi_pieza.json --out salida/mi_pieza
python3 scripts/music.py salida/mi_pieza                          # opcional
python3 scripts/render.py salida/mi_pieza --workers 4 --music salida/mi_pieza/music.wav
python3 scripts/qa.py salida/mi_pieza --originales carpeta_laminas_originales/
```

El render toma unos 4 minutos para 38 s de video con 6 procesos en paralelo; es normal.
