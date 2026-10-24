# Prompts

Todo en inglés (el modelo responde mejor), todo termina en `No text, no logos.` Describe a cada personaje con sus rasgos fijos cada vez, aunque vaya la hoja de referencia: el modelo se apoya en ambos.

Rasgos fijos del elenco de la intro:
- **protagonista** (la caricatura del creador): `boy with messy black hair, white round face, black oversized t-shirt, blue denim shorts, white sneakers`
- **espectador**: `big round white head with three hair sprouts, mustard-yellow t-shirt, blue denim shorts, white sneakers, thin stick arms and legs`
- **roles**: `white round heads, thick black stick limbs, white gloves, white shirts with mustard-yellow ties` (programador con lentes redondos y laptop gris; editor con audífonos al cuello y claqueta; diseñador con boina negra, lápiz amarillo gigante y paleta)
- **robot**: `small friendly white box-shaped robot with a dark screen face with white oval eyes and a yellow antenna bulb, half their height`

## Hoja de personajes (nuevo personaje)

`nano_banana_2_lite`, 16:9, la imagen original como `image_references`.

```
Character model sheet of the EXACT character in the reference image, same design and same clean hand-drawn cartoon style: bold smooth black outlines, flat colors, <rasgos>. Pure white seamless background with a soft gray ground shadow under each figure. Top row: the same character full body five times evenly spaced — front view, three-quarter view, side profile, back view, and <pose característica>. Bottom row: four head-and-shoulders close-ups of the same character with expressions: happy smile, surprised open mouth, thinking with hand on chin, laughing with eyes closed. Identical character in every view, consistent proportions. No text, no labels, no logos, no watermark.
```

Para cambiar algo del diseño original (ej. color de playera) dilo explícito: `BUT wearing a mustard-yellow short-sleeve t-shirt (instead of black)`.

## Frame inicio

```
Use the exact character designs from the reference sheets (<rasgos de cada personaje>). <BLOQUE DEL ESTILO>. Background: <fondo>. Composition: <quién está dónde, de cuerpo completo o no, qué sostiene, qué expresión>. <tamaño: "Both characters small in the frame, lots of green space above and between them" | "Character occupies about 70 percent of the frame height">. No text, no logos.
```

Fondos:
- verde: `solid flat chroma-key green (pure #00FF00), perfectly uniform, no shadows, no floor, no gradient.`
- blanco: `pure white background with a soft gray ground shadow.`
- cuaderno: `warm beige textured paper background with subtle pencil hatching shadows, like an illustrated notebook page.`

Composición para que funcione detrás de la persona: personajes en los **extremos izquierdo y derecho**, el tercio central vacío (ahí va su cabeza). Para una escena que entra al frente: un solo personaje centrado, 1:1.

## Frame final (edición del inicio)

Mismo modelo, `medias` = job_id del frame inicio.

```
Edit this image: keep exactly the same character, same <estilo> style, same <fondo>, same framing and size. Change only <qué cambió>: <pose final, objetos que aparecieron o desaparecieron, expresión>. No text, no logos.
```

Si el final necesita a otro personaje en pantalla (ej. el espectacular muestra al protagonista), agrega su hoja como segunda referencia y di `Edit the first image: … the boy from the second reference image …`.

## Kling 3.0

`kling3_0`, `mode: pro`, `sound: off`, `duration` 3–6 (lo que dura la frase; luego se ajusta con `data-playback-rate` 1.1–1.4), `start_image` + `end_image`.

```
<MOVIMIENTO DEL ESTILO>. <acción 1>; <acción 2>; <acción 3 que termina en la pose del frame final>. Static camera, no zoom. <fondo: "The background stays a perfectly flat solid chroma-key green the whole time, no shadows, no new objects." | "Same beige paper background." | "White background stays clean.">
```

Reglas:
- Acciones concretas y en orden, con verbos físicos ("snips through the film strip in one decisive cut", "pulls the handle; the door bursts open"). Nada abstracto.
- Remata con un gesto de cierre (pulgar arriba, chef's kiss, puño arriba): da un final limpio para cortar.
- Si sale "Preset IN THE DARK recommended", reenvía con `declined_preset_id`.

## Ejemplos reales de la intro

| clip | colocación | inicio → final | prompt de Kling (resumen) |
|---|---|---|---|
| k01 tijeras | detrás, verde 16:9 | robot a la izquierda y el protagonista a la derecha sosteniendo una tira de película con tijeras gigantes | corta la tira de un tijeretazo, el robot atrapa el pedazo como trofeo, el protagonista hace "tijeritas" en el aire |
| k02 alivio | frente, verde 1:1 | espectador confundido con "?" → sonriendo con pulgar arriba | el "?" tiembla y revienta como burbuja, suspira aliviado, pulgar arriba |
| k03 buzón | pantalla completa, cuaderno | buzón mostaza a reventar → avalancha de cartas hasta las rodillas | jala la manija, la puerta revienta, las cartas vuelan en remolino, él se ríe con los brazos arriba |
| k04 a/b/c | tarjetas 9:16 | el protagonista saludando en 3 estilos (limpio, lápiz, gis) | saluda con un brinquito; en lápiz las líneas "hierven"; en gis sueltan polvo |
| k05 aplausos | detrás, verde 16:9 | espectador y robot en los extremos aplaudiendo | aplauden y rebotan, salen corazones naranjas que crecen y revientan, el foco del robot parpadea |
| k06 pizza | pantalla completa, blanco | pizza solo con salsa → pizza completa con ingredientes y estrellitas | la mira sin ganas, le echa queso, pepperoni, albahaca y estrellas doradas, chef's kiss |
| k07a avión | pantalla completa, blanco | el protagonista va a lanzar un avión de papel; tele y celular vacíos → ambos encendidos con caricaturas | el avión vuela en curva, entra a la tele, chispas saltan al celular y se llena cuadro por cuadro |
| k07b espectacular | pantalla completa, cuaderno | espectacular en blanco en una calle → encendido con la caricatura del protagonista | aprieta el control, el espectacular parpadea y se prende, los de abajo brincan y señalan |
| k08 roles | split, cuaderno 1:1 | los tres roles lado a lado | uno por uno presume su habilidad (teclea, cierra la claqueta, pinta) |
| k09 foco | detrás, verde 1:1 | el protagonista pensando con un foco apagado → foco prendido, puño arriba | golpea su barbilla, el foco parpadea y se prende, abre los ojos y brinca |
| k10 claqueta | pantalla completa, cuaderno | el protagonista con la claqueta abierta | la cierra de golpe, salen líneas de acción, corre fuera de cuadro a la derecha |

Prompts completos con sus parámetros (modelo, aspect, duración, medias): `references/intro-prompts.json`, en orden de etapa (hojas → frames inicio → frames final → Kling). Los IDs de `medias` son jobs de la cuenta del autor: en otra cuenta no sirven, sube tus propias imágenes.
