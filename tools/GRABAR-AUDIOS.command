#!/bin/bash
#
#  Grabar los audios de Listening  ·  para Mac
#
#  Haz DOBLE CLIC en este archivo desde el Finder. No hay que escribir nada.
#
#  La primera vez tarda un poco mas porque prepara las herramientas.
#  Despues graba los 60 audios (unos 30 minutos) y, si esta carpeta viene de
#  GitHub, los sube el solo.
#

set -u
cd "$(dirname "$0")/.." || exit 1

pausa() { echo; read -n 1 -s -r -p "Pulsa cualquier tecla para cerrar esta ventana."; echo; }

echo "==========================================================="
echo "   Grabando los audios de Listening de NURIA CALVO ACADEMY"
echo "==========================================================="
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "No encuentro Python 3 en este Mac."
  echo
  echo "Se instala solo, una vez: abre la aplicacion Terminal, escribe"
  echo
  echo "    python3"
  echo
  echo "y pulsa Enter. Saldra una ventana ofreciendote instalar las"
  echo "herramientas de desarrollo: acepta, espera a que termine y vuelve"
  echo "a hacer doble clic en este archivo."
  pausa
  exit 1
fi

VENV=".venv-audio"
if [ ! -d "$VENV" ]; then
  echo "Preparando las herramientas (esto solo pasa la primera vez)..."
  if ! python3 -m venv "$VENV"; then
    echo "No he podido preparar el entorno de Python."
    pausa
    exit 1
  fi
fi

echo "Comprobando el generador de voz..."
if ! "$VENV/bin/python" -m pip install --quiet --upgrade pip edge-tts; then
  echo
  echo "No he podido instalar el generador de voz."
  echo "Suele ser falta de conexion a internet. Comprueba la wifi y reintenta."
  pausa
  exit 1
fi

echo
"$VENV/bin/python" tools/build_audio.py "$@"
ESTADO=$?
echo

if [ $ESTADO -ne 0 ]; then
  echo "La grabacion no ha terminado bien. Los mensajes de arriba dicen por que."
  echo "Puedes volver a hacer doble clic: continuara por donde se quedo."
  pausa
  exit $ESTADO
fi

if [ -d .git ] && command -v git >/dev/null 2>&1; then
  echo "Subiendo los audios a GitHub..."
  git add audio
  if git diff --staged --quiet; then
    echo "No habia audios nuevos que subir."
  elif git commit -q -m "Audios de Listening" && git push -q; then
    echo "LISTO. Los audios ya estan en GitHub y la aplicacion los usara sola."
  else
    echo "Los audios estan grabados en la carpeta  audio/  pero no he podido"
    echo "subirlos a GitHub. Puedes subirlos a mano desde la web del repositorio."
  fi
else
  echo "LISTO. Los audios estan en la carpeta  audio/"
  echo
  echo "Para publicarlos: entra en la pagina del repositorio en GitHub,"
  echo "pulsa 'Add file' > 'Upload files' y arrastra ahi la carpeta  audio/"
fi

pausa
