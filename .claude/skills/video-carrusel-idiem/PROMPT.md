# Prompts para el workstation

## 1. Instalación (una sola vez)

```
Instala la skill que está en video-carrusel-idiem/: cópiala completa a .claude/skills/video-carrusel-idiem/
de este repositorio, instala sus dependencias (sección "Comandos" del SKILL.md) y valida la instalación
regenerando el ejemplo: build + render + qa con config/ejemplo_sim.json y ejemplo/laminas_originales/.
Muéstrame qa/comparacion.jpg y no modifiques nada de la plantilla ni de los scripts.
```

## 2. Cada vez que quieras un video

```
Usa la skill video-carrusel-idiem para convertir en video el post [NÚMERO / FECHA] del workstation de [MES].
- Textos: literales de las láminas aprobadas, con sus mismos saltos de línea. No reescribas nada.
- Foto: la original de la librería según la traza del post ([CÓDIGO DE FOTO]); si no la encuentras, avísame
  antes de usar el plan B de limpiar_portada.py.
- Música: [sí / no].
- Antes de renderizar, muéstrame el JSON de configuración y la duración calculada.
- Entrega video.mp4 (+ video_musica.mp4 si pedí música), video.html y las dos hojas de QA,
  más una nota con todo lo que difiera de las láminas originales.
```
