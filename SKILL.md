---
name: broll-animado
description: Anima el B-roll de un video tipo talking head con personajes caricatura consistentes — plantilla de personajes, frames inicio/final con Nano Banana, animación con Kling 3.0 start+end vía el MCP de Higgsfield, fondo verde quitado con Python, sandwich (el B-roll pasa detrás de la persona, que queda recortada encima) y montaje en HyperFrames con subtítulos palabra por palabra y efectos de sonido calibrados contra la voz. 13 estilos — intro (default) + 3D película, anime, plastilina, caricatura 1930, acuarela, pixel art, papel recortado, cómic, low-poly, neón, pizarrón y motion plano. Úsalo cuando el usuario diga "anima el b-roll de este video", "b-roll animado", "b-roll con personajes", "hazme las animaciones de este video", "en estilo anime/plastilina/…", "sandwich con b-roll", o invoque /broll-animado.
---

# B-roll animado

Pipeline para meterle B-roll animado a un video donde alguien habla a cámara: personajes caricatura que actúan lo que se dice, algunos detrás de la persona (sandwich), otros al frente o a pantalla completa, con subtítulos y efectos de sonido. Nació en la intro de un video de Horizontes IA ("Cómo creo mis animaciones B-roll", oct 2026). El usuario da su video crudo (o solo un guion) y el skill entrega el video montado, o solo los clips si eso pide.

Archivos del skill:

| Ruta | Qué es |
|---|---|
| `references/estilos.md` | Los 13 estilos: bloque de estilo, cómo se mueve en Kling, si sirve con fondo verde |
| `references/prompts.md` | Plantillas de prompt (hoja de personajes, frame inicio, frame final, Kling) + ejemplos de la intro |
| `references/composicion.md` | Capas en HyperFrames (detrás / recorte / frente / pantalla completa / tarjetas / split), transiciones y trampas |
| `references/intro-prompts.json` | Los 38 prompts reales de la intro con sus parámetros |
| `assets/plantilla/` | El elenco de ejemplo: protagonista, espectador, roles, robot y elenco junto, + las refs originales |
| `assets/estilos/` | Un cuadro de muestra por estilo (mismo personaje en un avión de papel) |
| `assets/ejemplo-intro.html` | La composición real de la intro, para copiar patrones |
| `assets/fonts/` | Anton, Caveat 700 y DM Sans (licencia OFL) |
| `scripts/` | `transcribir.py`, `key_green.py`, `captions.py`, `eb_get.py`, `sfx_plan.py`, `build.py`, `hoja.py` |

## Requisitos

Revísalos la primera vez y di qué falta, con el comando para instalarlo:
- **MCP de Higgsfield** conectado (tools `generate_image_batch`, `generate_video_batch`, `jobs_wait`, `media_upload`, `media_confirm`) y créditos en la cuenta.
- **AssemblyAI**: `ASSEMBLYAI_API_KEY` en el entorno o en `~/.config/broll-animado/keys.env`.
- **Node.js 18+** (para `npx hyperframes`), **ffmpeg**, **Python 3** con `numpy` y `Pillow`.
- Opcional: **EditorBrain** CLI para su banco de efectos de sonido. Sin él, el usuario pone sus propios `.wav` en `assets/sfx/`.

## Reglas duras

- **Generación solo con el MCP de Higgsfield.** Antes de un lote, `get_cost: true` en una llamada suelta y di el total estimado.
- **Cero logos y marcas reales** en lo generado: cada prompt termina en `No text, no logos.` Dispositivos genéricos. Nada que parezca el logo de una plataforma (ej. rectángulo rojo + triángulo blanco). Nada de personajes con derechos de terceros.
- **Paleta por default**: neutros, negro, crema, con acentos amarillo mostaza / naranja. Si el usuario tiene colores de marca, usa los suyos.
- **Transcripción con AssemblyAI** (`scripts/transcribir.py`): da tiempos por palabra confiables en español. No uses Whisper para sincronizar.
- **Movimiento con sentido**: cada escena ilustra la frase que se dice en ese momento con UNA acción clara. Para eso, frame inicio + frame final y Kling interpola entre los dos. Cámara estática siempre.
- **El proyecto de HyperFrames va en el disco interno.** En discos exFAT (externos formateados para Mac+Windows) `hyperframes init` falla porque no soportan hard links. Los clips y el render final sí pueden vivir en un disco externo.
- **Un solo checkpoint**: el plan de escenas (paso 2), antes de gastar créditos. Después de eso, corre todo hasta el render.

## Entradas

Pregunta solo lo que falte, una cosa a la vez:
1. **Video crudo** (.mp4) o, si no hay, el guion. Sin talking head no hay sandwich: solo escenas a pantalla completa.
2. **Estilo** — default `intro`. Si el usuario nombra uno de `references/estilos.md`, usa ese. Se pueden mezclar (ej. tarjetas con 3 estilos para hablar de "estilos").
3. **Formato** — 16:9 por default; 9:16 si es reel.
4. **Personaje** — lo ideal es la caricatura del propio usuario: pídele una foto o un dibujo y haz su hoja (paso 3). Si no quiere, usa el elenco de `assets/plantilla/`.

## Flujo

### 0 · Carpetas

```bash
SLUG=<kebab-case>               # ej. intro-mi-video
A=~/Videos/broll-animado/$SLUG  # clips y render (puede ser un disco externo)
mkdir -p $A/{raw,transcript,frames,escenas/{stills,clips,keyed},matte}
```

### 1 · Transcripción

```bash
ffmpeg -v error -y -i "<video>" -vn -ac 1 -ar 16000 $A/raw/audio.wav
python3 ~/.claude/skills/broll-animado/scripts/transcribir.py $A/raw/audio.wav $A/transcript/raw.json
for t in 2 10 20 30; do ffmpeg -v error -y -ss $t -i "<video>" -frames:v 1 -vf scale=960:-1 $A/frames/f_$t.jpg; done
```

Mira los frames (encuadre, de qué lado queda espacio libre, color del fondo): eso decide dónde caben las escenas "detrás".

### 2 · Plan de escenas (CHECKPOINT)

Una escena por idea o analogía, más o menos cada 2–4 s de voz. Tabla para el usuario:

| # | t inicio–fin | frase | idea visual | colocación | personaje | fondo | Kling (s) |
|---|---|---|---|---|---|---|---|

Colocación (detalle en `references/composicion.md`):
- **detrás** — B-roll en fondo verde, keyed, entre el fondo y el recorte de la persona (sandwich). Para reacciones cortas (aplausos, tijeras, un foco que se prende).
- **frente** — personaje keyed tipo sticker con borde blanco, en una esquina, sin tapar la cara.
- **pantalla completa** — escena con fondo propio (papel crema, blanco) para analogías (buzón, pizza, avión de papel, espectacular).
- **tarjetas** — 2–3 clips verticales en cards sobre fondo negro (ej. "en cualquier estilo").
- **split** — la persona se corre a un lado y entra un panel (ej. "no ocupas ser programador/editor/diseñador" con tachones).
- **texto sandwich** — palabras gigantes detrás de la cabeza ("B | cabeza | ROLL"), sin generación.

Costo estimado (precios de oct 2026, confírmalos con `get_cost`): Nano Banana 2 Lite = 1 crédito por imagen, Nano Banana Pro 2k = 2, Kling 3.0 pro ≈ 1.75 créditos por segundo (5 s = 8.75). Suma imágenes (inicio + final por escena) + segundos de Kling y ponlo en la tabla.

Espera el OK del usuario. Ajusta y sigue.

### 3 · Plantilla de personajes

Personaje del usuario: sube su foto/dibujo (`media_upload` → `curl -X PUT -H "Content-Type: image/png" --data-binary @archivo` a la URL firmada → `media_confirm`) y haz la hoja con `nano_banana_2_lite`, 16:9, la plantilla "Hoja de personajes" de `references/prompts.md`. Revisa con Read que sea el mismo diseño en todas las vistas antes de seguir.

Elenco de ejemplo: sube las hojas de `assets/plantilla/` de la misma forma.

Estilo ≠ intro: genera primero UNA hoja del personaje en ese estilo (Nano Banana Pro, con la hoja del personaje + el cuadro de `assets/estilos/<estilo>.jpg` subido como referencias) y úsala como plantilla de todo el video. Así todas las escenas comparten diseño.

### 4 · Frames de inicio

`generate_image_batch`, un request por escena:
- estilo intro → `nano_banana_2_lite` (solo 1k, sobra para Kling); otros estilos → `nano_banana_pro` 2k.
- `aspect_ratio` según colocación: detrás/pantalla completa 16:9, personaje solo 1:1, tarjetas 9:16.
- `medias`: la hoja de personajes como `image_references` (+ cuadro del estilo si aplica).
- Prompt con la plantilla "Frame inicio" de `references/prompts.md`. Para detrás/frente: **fondo verde #00FF00 plano, sin sombras ni piso**, personajes chicos y en los extremos para que no choquen con la cabeza de la persona.

`jobs_wait` acepta máximo 12 jobs y espera ~15 s por llamada: repite hasta que terminen. Descarga a `$A/escenas/stills/kNN-<nombre>-ini.png`, arma una hoja de contacto y revísala con Read:

```bash
python3 ~/.claude/skills/broll-animado/scripts/hoja.py --images "$A/escenas/stills/*.png" -o $A/escenas/hoja-stills.jpg
```

Regenera lo que salga con texto, logos, otro diseño de personaje o fondo verde sucio.

### 5 · Frames finales

Edita el inicio en vez de generar de cero: mismo modelo, `medias` = job_id del frame inicio como `image_references`, prompt "Edit this image: keep exactly the same character, same style, same background, same framing and size. Change only …" (plantilla en `references/prompts.md`). Escenas que solo hacen un gesto en loop (saludar, aplaudir) pueden ir sin frame final.

### 6 · Animación con Kling 3.0

`generate_video_batch` con `model: kling3_0`, `mode: pro`, `sound: off`, `duration` 3–6, el mismo `aspect_ratio` del frame, `medias`: `start_image` (+ `end_image`). Prompt con la plantilla "Kling" de `references/prompts.md`: movimiento del estilo + acciones en orden + `Static camera, no zoom.` + (si es verde) `The background stays a perfectly flat solid chroma-key green the whole time, no shadows, no new objects.`

Trampa: a veces Higgsfield responde "Preset IN THE DARK recommended" en lugar de correr Kling → reenvía el mismo request con `declined_preset_id` igual al id del preset que sugirió.

Descarga a `$A/escenas/clips/kNN-<nombre>.mp4` y revisa inicio, mitad y final de cada clip:

```bash
python3 ~/.claude/skills/broll-animado/scripts/hoja.py --video $A/escenas/clips/k01-x.mp4 -o /tmp/k01.jpg
```

Que la acción tenga sentido y el personaje no se deforme. Rehaz con otro prompt lo que falle.

### 7 · Quitar el verde

```bash
python3 ~/.claude/skills/broll-animado/scripts/key_green.py $A/escenas/clips/k01-x.mp4 $A/escenas/keyed/k01-x.webm [--size 1920x1080]
```

Key por dominancia de verde (`g − max(r,b)`) + despill → WebM VP9 con alpha. Revisa un cuadro sobre fondo oscuro: si queda halo verde, baja `--t1` (default 60); si se come bordes negros finos, sube `--t0` (default 18). Neón y pizarrón no usan verde: ver `references/estilos.md`.

### 8 · Recorte de la persona (solo si hay sandwich)

```bash
npx --yes hyperframes remove-background "<video>" -o $A/matte/persona-alpha.webm --quality best > $A/matte/log.txt 2>&1
```

≈ 2.5 min por 45 s de video en una Mac con Apple Silicon. Córrelo en background mientras se generan las escenas.

### 9 · Montaje en HyperFrames

Si el usuario tiene los skills de HyperFrames, carga `hyperframes` antes de escribir HTML (si no: `npx hyperframes skills update`). Luego:

```bash
mkdir -p ~/Documents/edicion && cd ~/Documents/edicion
npx --yes hyperframes init $SLUG --non-interactive --example=blank --skill=general-video
cd $SLUG && mkdir -p assets/{video,broll,fonts,sfx} scripts transcript
cp "<video>" assets/video/santi.mp4 && cp $A/matte/persona-alpha.webm assets/video/santi-alpha.webm
cp $A/escenas/keyed/*.webm $A/escenas/clips/*.mp4 assets/broll/
cp $A/transcript/raw.json transcript/
cp ~/.claude/skills/broll-animado/assets/ejemplo-intro.html scripts/index.template.html
cp ~/.claude/skills/broll-animado/assets/fonts/*.woff2 assets/fonts/
```

(El ejemplo espera `assets/video/santi.mp4` y `santi-alpha.webm`; cambia los nombres en el HTML si prefieres otros.)

Reescribe `scripts/index.template.html` con las escenas de este video siguiendo `references/composicion.md` (capas, tiempos con la transcripción, transiciones). Subtítulos:

```bash
python3 ~/.claude/skills/broll-animado/scripts/captions.py --hide 16.95-17.8,23.5-24.6 --fix "aún=>¿aún|sabes,=>sabes?"
```

`--hide` = ventanas donde manda el texto cinético; `--fix` = correcciones de palabra (AssemblyAI pierde signos de pregunta). Corre desde la raíz del proyecto.

### 10 · Efectos de sonido

Pocos (≈ 1 cada 3 s, solo en acentos visuales) y siempre por debajo de la voz.

- **Con EditorBrain**:
  ```bash
  cd /tmp && editorbrain sfx search --project <eb-project> --bank editorbrain-essentials-v1 --query "paper swoosh" --scene-role body
  cd ~/Documents/edicion/$SLUG && python3 ~/.claude/skills/broll-animado/scripts/eb_get.py --project <eb-project> --catalog <sha256 del search> sfx-xxxx sfx-yyyy
  ```
- **Con tus propios sonidos**: copia los `.wav` a `assets/sfx/` (el `soundId` es el nombre del archivo sin extensión).

Escribe `transcript/sfx-cues.json` (formato en el docstring de `sfx_plan.py`): por cue, segundo, sonido y dB bajo la voz (acentos 11, barridos/papel 14, trazos 13). Luego:

```bash
python3 ~/.claude/skills/broll-animado/scripts/sfx_plan.py
python3 ~/.claude/skills/broll-animado/scripts/build.py
```

`sfx_plan.py` aplica el tope más estricto entre: loudness momentáneo (400 ms) bajo la voz, **pico ≤ voz − 12 dB** y **RMS de 50 ms ≤ voz − 15 dB**, y resta 3 dB a los archivos mono (HyperFrames los reproduce más fuerte). Si el usuario dice que alguno suena fuerte, súbele el `below` a ese cue, no a todos.

### 11 · Check, render y entrega

```bash
npm run check
npm run render -- -o renders/$SLUG-v1.mp4 --fps 30 --skill general-video > renders-log.txt 2>&1
```

Corre el render en background. Después:
1. Loudness a −14 LUFS / −1.5 dBTP con `loudnorm` de dos pasadas (medir → aplicar), copiando el video sin recodificar.
2. Hoja de contacto de cuadros clave (`scripts/hoja.py --video renders/... --at 1.6,6.6,11.8,…`) y revísala con Read: escenas en su lugar, sandwich limpio (sin bordes del recorte), subtítulos que no tapan nada.
3. Copia el final a `$A/$SLUG-FINAL.mp4` y ábrelo.

## Trampas conocidas

- **GSAP `fromTo` con `immediateRender`**: aplica el estado "from" desde el segundo 0, no desde su inicio. Un flash blanco hecho con `fromTo` lavó todo el video. Úsalo solo si el "from" es el estado que el elemento ya tiene antes de entrar (opacity 0 → 1 en algo que empieza invisible). Para todo lo demás: `tl.set` + `tl.to`.
- **Texto sandwich**: mide dónde está la cabeza de la persona (en la intro x ≈ 740–1170 px) y pon las palabras a los lados ("B" | cabeza | "ROLL"), no encima.
- **AssemblyAI parte "B-roll"** en "B" + "roll": `captions.py` lo une.
- **Archivos mono** suenan ~3 dB más en HyperFrames: `sfx_plan.py` los mide en estéreo y los compensa.
- **El loudness momentáneo subestima golpes cortos** (clics, impactos, cámara): por eso los topes de pico y RMS 50 ms.
- **Recorte de la persona**: muéstralo solo en las ventanas sandwich (`scene("#mattewrap", a, b)`); fuera de ellas el video base ya la tiene y el doble recorte se nota en los bordes.
