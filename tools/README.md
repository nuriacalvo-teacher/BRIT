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

Hace falta Python 3 y conexión a internet. Desde la carpeta del proyecto:

```bash
pip install edge-tts
python3 tools/build_audio.py
```

Tarda unos minutos (son 60 audios, unos 80 minutos de voz en total) y deja
en `audio/` un `.mp3` por unidad más un `manifest.json`.

**No hay que tocar `index.html`.** La aplicación busca `audio/manifest.json` al
arrancar: si existe usa las grabaciones, y si no existe sigue usando la voz del
navegador. Basta con subir la carpeta `audio/` junto al `index.html`.

### Opciones

```bash
python3 tools/build_audio.py --list-voices          # ver las voces británicas disponibles
python3 tools/build_audio.py --only listening_b1_t1 # regrabar una sola unidad
python3 tools/build_audio.py --force                # regrabar todo desde cero
```

Si se interrumpe a medias, se puede volver a lanzar: continúa por donde iba.

### Si cambias el texto de un diálogo

Regraba solo esa unidad:

```bash
python3 tools/build_audio.py --only listening_b2_t14 --force
```

## Voces

Se usan cuatro voces neuronales británicas, dos por interlocutor para que no se
confundan:

| Interlocutor | Voz femenina | Voz masculina |
|---|---|---|
| El del papel "0" (presentador, profesor, recepcionista…) | `en-GB-SoniaNeural` | `en-GB-RyanNeural` |
| El del papel "1" (el invitado, el alumno…) | `en-GB-LibbyNeural` | `en-GB-ThomasNeural` |

El género se deduce del nombre del personaje (las listas `FEMALE` y `MALE` están
al principio de `build_audio.py`, se pueden editar). Los papeles genéricos sin
nombre propio se reparten solos de forma estable.

## Qué hacer si no se puede generar el audio

La aplicación sigue funcionando con la voz del navegador, y dentro del
reproductor, en **"Ajustes de voz"**, muestra a cada alumno las instrucciones de
su dispositivo. En iPhone y iPad merece mucho la pena hacerlo una vez:

> **Ajustes → Accesibilidad → Contenido hablado → Voces → Inglés**, elegir por
> ejemplo *Daniel (Reino Unido)* y descargar la versión **Mejorada** o
> **Premium**. Después, recargar la página y seleccionarla en la lista.

La diferencia entre la voz compacta y la mejorada es justo la diferencia entre
"robot enlatado" y una voz normal.
