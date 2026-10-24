# Composición en HyperFrames

Base: `assets/ejemplo-intro.html` (una intro real de 45 s, 1920×1080). Cópialo a `scripts/index.template.html`, borra las escenas que no aplican y reutiliza los patrones. `scripts/build.py` inyecta subtítulos (`__CAPTIONS__`) y SFX (`<!--SFX-->`) y escribe `index.html`. Carga el skill `hyperframes` antes de editar.

## Capas (de atrás hacia adelante)

```
#root
 └ #cam                      ← cámara: punches y split mueven todo junto
    ├ #base   video de la persona (con audio)
    ├ #behind  B-roll keyed detrás de la persona + texto sandwich
    ├ #mattewrap  santi-alpha.webm (su recorte), visible solo en ventanas sandwich
    └ stickers al frente (#s2wrap…)
 ├ .scene  escenas a pantalla completa (fuera de #cam)
 ├ paneles split (#roles-panel)
 ├ #flash, #caps (subtítulos), #fadeout
 └ <audio> SFX
```

- **Sandwich** = `#behind` + `#mattewrap`. El recorte solo se muestra en las ventanas donde hay algo detrás:
  ```js
  [[0, 2.9], [12.35, 14.15]].forEach(([a, b]) => scene("#mattewrap", a, b));
  ```
- **Detrás**: `<video class="clip fill" src="assets/broll/k01.webm" muted playsinline data-start data-duration [data-playback-rate] [data-media-start]>` dentro de un wrapper; entra con `back.out(2)` de escala 0.92 → 1.
- **Frente (sticker)**: wrapper con clase `.sticker` (borde blanco con 4 `drop-shadow` + sombra). Entra con escala 0.5 → 1 y rotación −8 → 0. Nunca encima de la cara.
- **Pantalla completa**: `.scene` (opacity 0) + `scene(sel, inicio, fin)`. Transiciones usadas: iris `clipPath: circle(0% → 80%)`, wipe desde arriba `inset(0 0 100% 0) → inset(0)`, whip lateral `x: 1920 → 0` con `skewX: -10 → 0`, salida empujando `x: -1920`.
- **Tarjetas**: fondo `#est-back` que sube (`yPercent: 100 → 0`) y 3 `.card` (520×924, borde blanco 8 px, radio 26) que caen desde `y: -1150` con rotaciones −6/2/7, escalonadas 0.12 s.
- **Split**: `#cam` se corre `x: -480`, entra un panel de 960 px por la derecha con fondo `.paper`; los subtítulos (`#caps`) se corren igual. Tachones en SVG con `strokeDasharray/strokeDashoffset`.
- **Capas 3D** (para explicar que el B-roll va encima del video): dos `.plane` en un stage con `perspective` que se inclina (`rotationX: 50, rotationZ: -26`) y separa en `z`.
- **Texto cinético**: `.kin` (Anton, amarillo `#ffc21a`, contorno `#141414` de 14 px con `paint-order: stroke fill`, sombra sólida abajo). Entra con escala 0.3 → 1, `back.out(2.4)`. Para sandwich, mide la cabeza y reparte las palabras a los lados.
- **Etiquetas**: `.tag` (Caveat 78 px, fondo amarillo o blanco, borde de 6 px, sombra sólida) + flecha SVG a mano.

## Cámara

Punches cortos sincronizados a palabras clave: `scale 1 → 1.12` en 0.18 s `power3.out`, luego deriva lenta. Regresa a `scale: 1` con `tl.set` en un corte, nunca con un tween largo que se vea.

## Subtítulos

`scripts/captions.py` agrupa palabras de AssemblyAI en frases de ≤ 4 palabras, corta en pausas > 0.22 s o puntuación, une "B" + "roll", y oculta las ventanas `--hide` donde manda el texto cinético. En la plantilla: DM Sans 800 a 64 px, blanco con contorno negro, la palabra activa en amarillo y escala 1.08.

## Fuentes

Copia `~/.claude/skills/broll-animado/assets/fonts/` (Anton, Caveat 700, DM Sans variable) a `assets/fonts/` del proyecto. Para otra fuente, bájala de Google Fonts en woff2 al mismo lugar: HyperFrames renderiza sin red.

## Trampas

- **`fromTo` aplica el "from" desde el segundo 0** (immediateRender). Un `#flash` con `fromTo({opacity: 0.9}, {opacity: 0})` dejó todo el video blanco. Úsalo solo cuando el "from" ya es el estado del elemento antes de entrar (opacity 0 de algo invisible). Si no: `tl.set(sel, {opacity: 0.9}, t); tl.to(sel, {opacity: 0, …}, t)`.
- **Un solo timeline pausado** registrado en `window.__timelines["main"]`. Nada de `Math.random()` ni `Date.now()`.
- **Videos con alpha**: WebM VP9 `yuva420p`. Un MP4 no trae alpha.
- **`data-playback-rate`** 1.1–1.4 acelera clips de Kling que quedaron lentos; no pases de 1.4, se nota.
- **Proyecto en un disco exFAT** (discos externos formateados para Mac+Windows): `hyperframes init` falla porque exFAT no soporta hard links. Crea el proyecto en el disco interno.
- Corre `npm run check` después de cada cambio y antes de renderizar.
