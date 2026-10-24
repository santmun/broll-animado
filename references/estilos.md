# Estilos

13 opciones. `intro` es el default y el único probado de punta a punta (intro de oct 2026). Los otros 12 salieron de una librería hecha con Nano Banana Pro: el mismo personaje volando en un avión de papel. Su muestra está en `assets/estilos/` (vista de todos juntos: `docs/estilos.jpg` en el repo).

Cómo usar un estilo:
- **Frame (still)**: arranca el prompt con su **bloque**, reemplazando `<CAST>` por la descripción del/los personajes y luego la escena.
- **Kling**: arranca el prompt de animación con su **movimiento**.
- **Referencias**: hoja de personajes + el cuadro de muestra del estilo (súbelo con `media_upload`) para que el look no se desvíe.
- **Fondo**: la columna "verde" dice si el estilo se puede keyear para ir detrás/al frente de la persona.

| clave | estilo | verde | muestra |
|---|---|---|---|
| `intro` | caricatura limpia (default) | ✅ probado | `assets/plantilla/elenco.png` |
| `3d` | 3D de película | ⚠️ | `01-3d-pelicula.jpg` |
| `anime` | anime | ✅ | `02-anime.jpg` |
| `plastilina` | plastilina / stop-motion | ⚠️ | `03-plastilina.jpg` |
| `1930` | caricatura 1930 (rubber-hose) | ❌ | `04-caricatura-1930.jpg` |
| `acuarela` | acuarela | ❌ | `05-acuarela.jpg` |
| `pixel` | pixel art 16-bit | ✅ | `06-pixel-art.jpg` |
| `papel` | papel recortado | ⚠️ | `07-papel-recortado.jpg` |
| `comic` | cómic pop-art | ✅ | `08-comic.jpg` |
| `lowpoly` | low-poly | ⚠️ | `09-low-poly.jpg` |
| `neon` | neón synthwave | ❌ → negro + `screen` | `10-neon.jpg` |
| `pizarron` | pizarrón blanco (doodle con plumón) | ❌ → blanco + `multiply` | `11-pizarron.jpg` |
| `plano` | motion graphics plano | ✅ | `12-motion-plano.jpg` |

✅ keyea limpio · ⚠️ funciona si el prompt pide "no shadows, no ground, no glow" y revisas bordes; si no, úsalo a pantalla completa · ❌ solo pantalla completa o tarjetas (o el truco de blend indicado). Solo `intro` está probado con el keyer; las demás marcas son estimaciones por cómo se ve cada estilo: confírmalas con un clip de prueba.

## Bloques

### intro — caricatura limpia (default)
- **Bloque**: `Clean hand-drawn cartoon style, bold smooth black outlines, flat colors. <CAST>.` Fondos según colocación: verde `#00FF00` plano, blanco puro con sombra gris suave, o papel beige de cuaderno (`warm beige textured paper background with subtle pencil hatching shadows, like an illustrated notebook page`).
- **Movimiento**: `2D cartoon animation, same flat hand-drawn style.`
- **Modelo**: `nano_banana_2_lite` (1k).
- Variantes dentro del mismo estilo que se usaron en las tarjetas de la intro: boceto a lápiz (`rough graphite pencil sketch with crosshatching and visible construction lines on warm beige sketchbook paper, a touch of mustard-yellow colored pencil`, movimiento `boiling sketchy line style like a flipbook`) y gis en pizarrón (`white and yellow chalk drawing on a dark black-green chalkboard`, movimiento `chalk dust puffs as he moves`).

### 3d — 3D de película
- **Bloque**: `A single still frame from a high-end 3D animated feature film: <CAST> reimagined as polished 3D animated movie characters, cinematic soft lighting, subsurface skin.`
- **Movimiento**: `3D animated feature film animation, smooth cinematic character motion with gentle squash and stretch, same 3D look.`
- Verde: pide `no ground shadow, no rim glow`. Le queda mejor pantalla completa con su propio set.

### anime
- **Bloque**: `A single still frame from a Japanese anime TV series, cel-shaded with crisp linework: <CAST>.` Acentos: speed lines, sparkles, cielos con degradado.
- **Movimiento**: `Japanese anime animation, cel-shaded, snappy key poses with smear frames and speed lines, same anime style.`

### plastilina
- **Bloque**: `A single still frame from a claymation stop-motion film: <CAST> as plasticine clay puppets with visible fingerprints and handmade texture, warm practical studio lighting.`
- **Movimiento**: `Claymation stop-motion animation with a slightly choppy 12 fps feel, the clay keeps its fingerprints and texture.`
- Verde: pide `no shadows on the green`. Revisa que el key no se coma la textura de los bordes.

### 1930 — caricatura rubber-hose
- **Bloque**: `A single still frame from a 1930s black-and-white rubber-hose cartoon: <CAST> redrawn in vintage rubber-hose style with bendy limbs, pie-cut eyes and white gloves, film grain, scratches and vignette of an old film reel. Black and white only.`
- **Movimiento**: `1930s rubber-hose cartoon animation, bouncy looping limbs, black and white with film flicker and grain.`
- No va en verde (el modelo desatura todo). Pantalla completa o tarjeta.

### acuarela
- **Bloque**: `A single still frame from a hand-painted watercolor storybook animation: <CAST>, loose wet brushstrokes, paper texture, gentle pastel palette with warm orange accents.`
- **Movimiento**: `Hand-painted watercolor animation, painted frames with a gentle wet-paint shimmer, soft and slow motion.`
- Bordes húmedos = key imposible. Pantalla completa.

### pixel — pixel art 16-bit
- **Bloque**: `A single frame from a 16-bit retro video game: <CAST> as pixel-art sprites, crisp pixels, limited vibrant palette.` Sin números de score.
- **Movimiento**: `16-bit pixel-art sprite animation, few frames, crisp pixels, no smoothing or blur.`
- Kling a veces suaviza los píxeles: si pasa, escala el clip con `-vf scale=iw/4:ih/4:flags=neighbor,scale=iw*4:ih*4:flags=neighbor` antes del key.

### papel — papel recortado
- **Bloque**: `A single still frame from a paper cutout stop-motion animation: <CAST> built from layered cut colored paper and cardboard, visible paper edges and soft shadows between layers.`
- **Movimiento**: `Paper cutout stop-motion animation, flat paper pieces slide and rotate on their joints, slightly choppy.`
- Verde: pide `no drop shadows on the background`.

### comic — cómic pop-art
- **Bloque**: `A single panel-like frame from a pop-art comic book animation: <CAST>, bold black ink outlines, Ben-Day halftone dots.` Fondo de pantalla completa: `saturated yellow and red background with an explosive action burst shape`. Nunca onomatopeyas escritas.
- **Movimiento**: `Pop-art comic book animation, bold ink outlines and halftone dots stay crisp, punchy poses with action lines.`

### lowpoly
- **Bloque**: `A single frame from a low-poly 3D animation: <CAST> as faceted low-poly characters, clean flat-shaded polygons, soft gradient sky.`
- **Movimiento**: `Low-poly 3D animation, flat-shaded facets, clean simple motion.`

### neon — neón synthwave
- **Bloque**: `A single frame from a neon synthwave animation: <CAST> drawn only with glowing neon outlines (magenta, orange and yellow light lines) on a pure black background.`
- **Movimiento**: `Neon line animation, glowing lines trace and flicker, light streaks follow the motion, the background stays pure black.`
- Sin verde: genera sobre negro puro y en HyperFrames pon el clip con `style="mix-blend-mode: screen"`. El negro desaparece y el brillo se conserva.

### pizarron — pizarrón blanco
- **Bloque**: `A single frame from a whiteboard doodle explainer animation: <CAST> in simple black marker line art on a clean white board, a few touches of orange and yellow marker color.` Opcional: una mano real con plumón entrando por abajo.
- **Movimiento**: `Whiteboard doodle animation, marker lines draw themselves on and wiggle slightly like a living sketch.`
- Sin verde: genera sobre blanco puro y usa `mix-blend-mode: multiply` encima del video. El blanco desaparece y las líneas quedan.

### plano — motion graphics plano
- **Bloque**: `A single frame from a flat vector motion-graphics explainer animation: <CAST> simplified into bold geometric flat shapes, vibrant warm palette, subtle long shadows.`
- **Movimiento**: `Flat vector motion-graphics animation, smooth eased shape motion, clean geometric forms.`
