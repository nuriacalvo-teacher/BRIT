# Audio de los ejercicios de Listening

## El problema

La aplicación puede leer los diálogos de dos maneras:

1. **Con la voz del propio navegador** (Web Speech API). No hace falta nada más,
   pero **cada aparato trae voces distintas**:

   | Dispositivo | Qué voz sale de fábrica | Cómo suena |
   |---|---|---|
   | Mac | voces *enhanced* de Apple, y las de Google en Chrome | bien |
   | iPhone / iPad | voz **compacta** de Apple | metálica, "robot enlatado" |
   | Android | Google TTS | bien |
   | Windows | voces de Microsoft (Edge añade las *Online Natural*) | de correcto a muy bien |
   | Linux / Vitalinux | normalmente **ninguna**, o eSpeak | no suena, o suena a robot |

2. **Con audio grabado** (esta carpeta). Se graba una vez y **todos los alumnos
   oyen exactamente lo mismo**, en cualquier móvil, tablet u ordenador. Es la
   opción recomendada para usarlo en clase, sobre todo con los equipos Linux.

## Primero: oye las voces

Antes de grabar media hora de audio, escucha 30 segundos de muestra. Son
frases reales del material, con las mismas cuatro voces y el mismo reparto que
tendría la grabación de verdad.

- **En el Mac:** doble clic en `tools/ESCUCHAR-VOCES.command`. Tarda un minuto
  y abre el resultado en el reproductor.
- **Online:** pestaña **Actions** → *Grabar los audios de Listening* →
  **Run workflow**, marcando la casilla **muestra**. Al terminar, descarga
  *muestra-de-voces* desde la propia página de la ejecución.
- **Sin nada de esto:** son voces neuronales de Azure, las mismas que usa
  **Microsoft Edge** en su función *Leer en voz alta*. Abre Edge en cualquier
  página, clic derecho → *Leer en voz alta* → opciones de voz → elige
  **Sonia** o **Ryan** (Reino Unido). Eso es exactamente lo que vas a obtener.

La muestra no toca la aplicación ni el manifest: si no te convence, no has
perdido nada.

## Cómo generar el audio grabado

## Cómo generar el audio grabado

### Opción A · en el Mac, con doble clic (la más fiable)

1. Descarga el proyecto: en la página del repositorio, botón verde **Code** →
   **Download ZIP**. Descomprímelo.
2. Entra en la carpeta `tools` y haz **doble clic** en
   **`GRABAR-AUDIOS.command`**.
3. Se abre una ventana negra y empieza a grabar. Déjala trabajar.

La primera vez puede pedirte instalar las herramientas de desarrollo de macOS:
acepta, espera, y vuelve a hacer doble clic. Si en vez del ZIP clonaste el
repositorio con `git`, al terminar sube los audios él solo.

> Si macOS dice que *no se puede abrir porque proviene de un desarrollador no
> identificado*: clic derecho sobre el archivo → **Abrir** → **Abrir**. Solo la
> primera vez.

### Opción B · online, sin instalar nada

1. Pestaña **Actions** del repositorio.
2. **Grabar los audios de Listening** en la lista de la izquierda.
3. **Run workflow** → **Run workflow**.

Corre en los servidores de GitHub y sube los audios él solo. Puedes cerrar la
pestaña. Es la opción más cómoda, pero el servicio de voz rechaza a veces las
peticiones que vienen de centros de datos; si falla con un error de permisos o
de conexión, usa la Opción A, que sale desde tu propia red.

> Si falla al subir los audios: **Settings → Actions → General → Workflow
> permissions → Read and write permissions**. Se toca una sola vez.

### Opción C · a mano, desde el terminal

```bash
python3 -m venv .venv-audio
.venv-audio/bin/pip install edge-tts
.venv-audio/bin/python tools/build_audio.py
git add audio && git commit -m "Audios de Listening" && git push
```

### En los tres casos

**No hay que tocar `index.html`.** La aplicación busca `audio/manifest.json` al
arrancar: si existe usa las grabaciones, y si no existe sigue usando la voz del
navegador.

Son 60 audios, unos 80 minutos de voz y unos 25 MB. Tarda alrededor de media
hora. Si se interrumpe se puede relanzar: continúa por donde iba.

### Regrabar una unidad concreta

Si cambias el texto de un diálogo:

```bash
.venv-audio/bin/python tools/build_audio.py --only listening_b2_t14 --force
```

En la Opción B esas mismas opciones aparecen como casillas al pulsar
**Run workflow**.

## Voces

Se usan voces neuronales británicas, y **cada interlocutor de una misma unidad
recibe una voz distinta** para que no se confundan:

| | Voces femeninas | Voces masculinas |
|---|---|---|
| Disponibles | `en-GB-SoniaNeural`, `en-GB-LibbyNeural`, `en-GB-MaisieNeural` | `en-GB-RyanNeural`, `en-GB-ThomasNeural` |
| Preferida para quien conduce (presentador, profesor, recepcionista…) | `Sonia` | `Ryan` |
| Preferida para quien responde (el invitado, el alumno…) | `Libby` | `Thomas` |

Si en una unidad dos personajes comparten papel —pasa en `listening_b2_t2`, que
tiene un presentador y dos invitados— el segundo recibe la siguiente voz libre
de su mismo género, nunca la que ya está en uso.

El género se deduce del nombre del personaje (las listas `FEMALE` y `MALE` están
al principio de `build_audio.py`, se pueden editar). Los papeles genéricos sin
nombre propio se reparten solos de forma estable: el mismo papel en la misma
unidad sale siempre con la misma voz.

## Qué hacer si no se puede generar el audio

La aplicación sigue funcionando con la voz del navegador, y dentro del
reproductor, en **"Ajustes de voz"**, muestra a cada alumno las instrucciones de
su dispositivo. En iPhone y iPad merece mucho la pena hacerlo una vez:

> **Ajustes → Accesibilidad → Contenido hablado → Voces → Inglés**, elegir por
> ejemplo *Daniel (Reino Unido)* y descargar la versión **Mejorada** o
> **Premium**. Después, recargar la página y seleccionarla en la lista.

La diferencia entre la voz compacta y la mejorada es justo la diferencia entre
"robot enlatado" y una voz normal.
