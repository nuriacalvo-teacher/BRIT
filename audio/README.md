# Carpeta de audio

Aquí van los audios grabados de los ejercicios de Listening.

Se generan de una de estas formas:

- **En el Mac:** doble clic en `tools/GRABAR-AUDIOS.command`.
- **Online:** pestaña **Actions** → *Grabar los audios de Listening* →
  **Run workflow**.

Contenido después de generarlos:

- `listening_b1_t1.mp3` … `listening_b2_t30.mp3` — un audio por unidad.
- `manifest.json` — índice con la duración de cada audio y el momento en que
  entra cada interlocutor (para el indicador de quién habla).

La aplicación busca `manifest.json` al arrancar. **Si esta carpeta está vacía no
pasa nada**: se usa la voz del navegador, como antes.

Ver `tools/README.md` para los detalles.
