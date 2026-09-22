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

## Cómo generar el audio grabado

### Opción A · desde la web de GitHub, sin instalar nada (recomendada)

1. Entra en la pestaña **Actions** del repositorio.
2. En la lista de la izquierda, elige **Grabar los audios de Listening**.
3. Botón **Run workflow** → **Run workflow**.

Tarda entre 20 y 40 minutos y puedes cerrar la pestaña: sigue corriendo en los
servidores de GitHub. Cuando termina, los audios ya están subidos al
repositorio y la aplicación los usa sola.

> Si el paso final falla con un error de permisos, entra en
> **Settings → Actions → General → Workflow permissions** y marca
> **Read and write permissions**. Es un ajuste que solo hay que tocar una vez.

### Opción B · desde tu ordenador

Hace falta Python 3 y conexión a internet. Desde la carpeta del proyecto:

```bash
pip install edge-tts
python3 tools/build_audio.py
```

Deja en `audio/` un `.mp3` por unidad más un `manifest.json`, que hay que subir
al repositorio (`git add audio && git commit -m "Audios" && git push`).

### En ambos casos

**No hay que tocar `index.html`.** La aplicación busca `audio/manifest.json` al
arrancar: si existe usa las grabaciones, y si no existe sigue usando la voz del
navegador.

Son 60 audios, unos 80 minutos de voz y unos 25 MB en total. Si el proceso se
interrumpe a medias se puede volver a lanzar: continúa por donde iba.

### Opciones de la línea de órdenes

```bash
python3 tools/build_audio.py --list-voices          # ver las voces británicas disponibles
python3 tools/build_audio.py --only listening_b1_t1 # regrabar una sola unidad
python3 tools/build_audio.py --force                # regrabar todo desde cero
```

En la Opción A esas mismas opciones aparecen como casillas al pulsar
**Run workflow**.

### Si cambias el texto de un diálogo

Regraba solo esa unidad:

```bash
python3 tools/build_audio.py --only listening_b2_t14 --force
```

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
