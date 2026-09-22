# Carpeta de audio

Aquí van los audios grabados de los ejercicios de Listening.

Se generan de una de estas dos formas:

- **Sin instalar nada:** pestaña **Actions** del repositorio → *Grabar los
  audios de Listening* → **Run workflow**.
- **Desde tu ordenador:**

  ```bash
  pip install edge-tts
  python3 tools/build_audio.py
  ```

Contenido después de generarlos:

- `listening_b1_t1.mp3` … `listening_b2_t30.mp3` — un audio por unidad.
- `manifest.json` — índice con la duración de cada audio y el momento en que
  entra cada interlocutor (para el indicador de quién habla).

La aplicación busca `manifest.json` al arrancar. **Si esta carpeta está vacía no
pasa nada**: se usa la voz del navegador, como antes.

Ver `tools/README.md` para los detalles.
