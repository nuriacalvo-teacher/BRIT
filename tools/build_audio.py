#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_audio.py · graba los audios de los ejercicios de Listening.

Por qué existe
--------------
La aplicacion puede leer los dialogos con la voz del propio navegador, pero
esa voz no es la misma en todos los aparatos: en un iPhone recien sacado de
la caja suena metalica, y en Linux muchas veces no hay ninguna voz instalada.
Este script graba los 60 audios una sola vez, con voces britanicas neuronales,
y a partir de ahi TODOS los alumnos oyen exactamente lo mismo, en iPhone,
Android, Windows, Vitalinux o Mac.

Uso
---
    pip install edge-tts
    python3 tools/build_audio.py

Deja los ficheros en audio/ junto con audio/manifest.json. La aplicacion
detecta ese manifest sola: si esta, usa las grabaciones; si no, sigue usando
la voz del navegador.

Opciones utiles
---------------
    --only listening_b1_t1 listening_b2_t7     graba solo esas unidades
    --force                                    regraba aunque ya existan
    --list-voices                              muestra las voces disponibles
"""

import argparse
import asyncio
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INDEX = os.path.join(ROOT, "index.html")
AUDIO_DIR = os.path.join(ROOT, "audio")

# Voces britanicas disponibles, por genero. Dentro de una misma unidad cada
# interlocutor recibe una voz distinta: hay un dialogo a tres (un presentador
# y dos invitados) en el que dos personajes comparten papel, y con solo dos
# voces sonarian iguales.
VOICE_POOL = {
    "f": ["en-GB-SoniaNeural", "en-GB-LibbyNeural", "en-GB-MaisieNeural"],
    "m": ["en-GB-RyanNeural", "en-GB-ThomasNeural"],
}
# Voz preferida segun el papel: 0 = quien conduce (presentador, profesor,
# recepcionista...), 1 = quien responde (el invitado, el alumno...).
PREFERRED_VOICE = {
    (0, "f"): "en-GB-SoniaNeural",
    (0, "m"): "en-GB-RyanNeural",
    (1, "f"): "en-GB-LibbyNeural",
    (1, "m"): "en-GB-ThomasNeural",
}

# Genero de los interlocutores con nombre propio. Los papeles genericos
# ("Host", "Teacher", "Receptionist"...) se reparten solos, mas abajo.
FEMALE = {
    "bea", "beatriz", "carmen", "clara", "claudia", "elena", "eva", "julia",
    "laura", "lidia", "lucía", "lucia", "marina", "marta", "ms vidal", "nuria",
    "pilar", "rosa", "sofía", "sofia",
}
MALE = {
    "alberto", "diego", "iván", "ivan", "martín", "martin", "mr espín",
    "mr espin", "rubén", "ruben", "sergio", "tomás", "tomas",
}

TURN_GAP = 0.65        # segundos de silencio al cambiar de interlocutor
SENTENCE_GAP = 0.0     # edge-tts ya deja su propia pausa al final de cada frase


# ---------------------------------------------------------------------------
# 1 · leer los dialogos de index.html
# ---------------------------------------------------------------------------
class JsLiteral(object):
    """Lector minimo de literales JavaScript: objetos con clave sin comillas,
    cadenas, numeros, true/false/null, comentarios y comas sobrantes."""

    def __init__(self, text):
        self.s = text
        self.i = 0

    def error(self, msg):
        line = self.s.count("\n", 0, self.i) + 1
        raise ValueError("%s (linea %d)" % (msg, line))

    def skip(self):
        while self.i < len(self.s):
            c = self.s[self.i]
            if c in " \t\r\n":
                self.i += 1
            elif self.s.startswith("/*", self.i):
                end = self.s.find("*/", self.i + 2)
                self.i = len(self.s) if end < 0 else end + 2
            elif self.s.startswith("//", self.i):
                end = self.s.find("\n", self.i)
                self.i = len(self.s) if end < 0 else end + 1
            else:
                return

    def value(self):
        self.skip()
        if self.i >= len(self.s):
            self.error("fin de fichero inesperado")
        c = self.s[self.i]
        if c == "{":
            return self.obj()
        if c == "[":
            return self.arr()
        if c in "\"'":
            return self.string()
        if self.s.startswith("true", self.i):
            self.i += 4
            return True
        if self.s.startswith("false", self.i):
            self.i += 5
            return False
        if self.s.startswith("null", self.i):
            self.i += 4
            return None
        m = re.match(r"-?\d+(\.\d+)?([eE][-+]?\d+)?", self.s[self.i:])
        if not m:
            self.error("valor no reconocido: %r" % self.s[self.i:self.i + 20])
        self.i += m.end()
        txt = m.group(0)
        return float(txt) if ("." in txt or "e" in txt or "E" in txt) else int(txt)

    def string(self):
        quote = self.s[self.i]
        self.i += 1
        out = []
        while True:
            if self.i >= len(self.s):
                self.error("cadena sin cerrar")
            c = self.s[self.i]
            if c == "\\":
                nxt = self.s[self.i + 1]
                self.i += 2
                if nxt == "u":
                    out.append(chr(int(self.s[self.i:self.i + 4], 16)))
                    self.i += 4
                else:
                    out.append({"n": "\n", "t": "\t", "r": "\r", "b": "\b",
                                "f": "\f", "0": "\0"}.get(nxt, nxt))
            elif c == quote:
                self.i += 1
                return "".join(out)
            else:
                out.append(c)
                self.i += 1

    def arr(self):
        self.i += 1                      # [
        out = []
        while True:
            self.skip()
            if self.s[self.i] == "]":
                self.i += 1
                return out
            out.append(self.value())
            self.skip()
            if self.s[self.i] == ",":
                self.i += 1
            elif self.s[self.i] != "]":
                self.error("se esperaba , o ]")

    def obj(self):
        self.i += 1                      # {
        out = {}
        while True:
            self.skip()
            if self.s[self.i] == "}":
                self.i += 1
                return out
            if self.s[self.i] in "\"'":
                key = self.string()
            else:
                m = re.match(r"[A-Za-z_$][A-Za-z0-9_$]*", self.s[self.i:])
                if not m:
                    self.error("clave no reconocida")
                key = m.group(0)
                self.i += m.end()
            self.skip()
            if self.s[self.i] != ":":
                self.error("se esperaba : tras la clave %r" % key)
            self.i += 1
            out[key] = self.value()
            self.skip()
            if self.s[self.i] == ",":
                self.i += 1
            elif self.s[self.i] != "}":
                self.error("se esperaba , o }")


def read_topics():
    src = io.open(INDEX, encoding="utf-8").read()
    start = src.find("var TOPICS = [")
    if start < 0:
        raise SystemExit("No encuentro 'var TOPICS = [' en index.html")
    reader = JsLiteral(src)
    reader.i = start + len("var TOPICS = ")
    return reader.arr()


def listening_units():
    """Devuelve [(unit_id, [(speaker, v, texto), ...]), ...] en el mismo orden
    en que la aplicacion los numera."""
    units = []
    for topic in read_topics():
        n = topic.get("n")
        for level in ("B1", "B2"):
            data = (topic.get(level) or {}).get("l")
            if not data or not data.get("ln"):
                continue
            unit_id = "listening_%s_t%s" % (level.lower(), n)
            lines = [(ln[0], int(ln[1]), ln[2]) for ln in data["ln"]]
            units.append((unit_id, lines))
    return units


def gender_for(speaker, v, unit_id):
    key = speaker.strip().lower()
    if key in FEMALE:
        return "f"
    if key in MALE:
        return "m"
    if key.startswith("ms ") or key.startswith("mrs ") or key.startswith("miss "):
        return "f"
    if key.startswith("mr "):
        return "m"
    # Papeles genericos: se reparten de forma estable (el mismo papel en la
    # misma unidad sale siempre con la misma voz) pero variada entre unidades.
    digest = hashlib.md5((unit_id + "|" + key).encode("utf-8")).hexdigest()
    return "f" if int(digest[:8], 16) % 2 else "m"


def assign_voices(unit_id, lines):
    """Una voz distinta por interlocutor dentro de la misma unidad."""
    used, mapping = set(), {}
    for speaker, v, _ in lines:
        if speaker in mapping:
            continue
        gender = gender_for(speaker, v, unit_id)
        pick = PREFERRED_VOICE[(1 if v else 0, gender)]
        if pick in used:                                   # ya la usa otro
            free = [x for x in VOICE_POOL[gender] if x not in used]
            if not free:                                   # sin voces de ese genero
                free = [x for x in VOICE_POOL["f"] + VOICE_POOL["m"] if x not in used]
            pick = free[0] if free else pick
        mapping[speaker] = pick
        used.add(pick)
    return mapping


# ---------------------------------------------------------------------------
# 2 · MP3 sin dependencias externas: duracion y silencio
# ---------------------------------------------------------------------------
BITRATES_V1 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
BITRATES_V2 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0]
RATES = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


def mp3_frames(data):
    """Recorre las tramas MPEG Layer III. Devuelve (offset, tamano, muestras,
    frecuencia). Se salta ID3 y cualquier basura entre tramas."""
    i = 0
    if data[:3] == b"ID3":
        size = 0
        for b in data[6:10]:
            size = (size << 7) | (b & 0x7F)
        i = 10 + size
    n = len(data)
    while i + 4 <= n:
        if data[i] != 0xFF or (data[i + 1] & 0xE0) != 0xE0:
            i += 1
            continue
        version = (data[i + 1] >> 3) & 0x03      # 3=MPEG1 2=MPEG2 0=MPEG2.5
        layer = (data[i + 1] >> 1) & 0x03        # 1 = Layer III
        if version == 1 or layer != 1:
            i += 1
            continue
        br_index = (data[i + 2] >> 4) & 0x0F
        sr_index = (data[i + 2] >> 2) & 0x03
        padding = (data[i + 2] >> 1) & 0x01
        if br_index in (0, 15) or sr_index == 3:
            i += 1
            continue
        rate = RATES[version][sr_index]
        bitrate = (BITRATES_V1 if version == 3 else BITRATES_V2)[br_index] * 1000
        samples = 1152 if version == 3 else 576
        size = (samples // 8) * bitrate // rate + padding
        if size < 4 or i + size > n:
            break
        yield i, size, samples, rate
        i += size


def mp3_info(data):
    """(duracion en segundos, frecuencia de muestreo)."""
    total, rate = 0, 24000
    for _, _, samples, sr in mp3_frames(data):
        total += samples
        rate = sr
    return (total / float(rate) if rate else 0.0), rate


def silence_mp3(seconds, rate=24000):
    """Tramas MPEG-2 Layer III mono vacias: se decodifican como silencio y se
    pueden pegar delante o detras de cualquier MP3 de la misma frecuencia."""
    sr_index = {22050: 0, 24000: 1, 16000: 2}.get(rate)
    if sr_index is None:                          # frecuencia rara: sin silencio
        return b""
    bitrate = 32000
    frame_len = (576 // 8) * bitrate // rate      # 96 bytes a 24 kHz
    header = bytes([
        0xFF,
        0b11110011,                               # MPEG2 · Layer III · sin CRC
        (4 << 4) | (sr_index << 2),               # 32 kbps · frecuencia · sin padding
        0b11000000,                               # mono
    ])
    frame = header + b"\x00" * (frame_len - 4)
    count = int(round(seconds / (576.0 / rate)))
    return frame * max(0, count)


# ---------------------------------------------------------------------------
# 3 · sintesis
# ---------------------------------------------------------------------------
async def synth(text, voice):
    import edge_tts
    chunks = []
    communicate = edge_tts.Communicate(text, voice)
    async for item in communicate.stream():
        if item["type"] == "audio":
            chunks.append(item["data"])
    if not chunks:
        raise RuntimeError("edge-tts no devolvio audio para la voz %s" % voice)
    return b"".join(chunks)


async def build_unit(unit_id, lines, force, existing):
    out_mp3 = os.path.join(AUDIO_DIR, unit_id + ".mp3")
    # Si ya esta grabado y el manifest conserva sus marcas de tiempo, se deja
    # como esta: asi se puede interrumpir y reanudar la grabacion.
    if os.path.exists(out_mp3) and not force and existing and existing.get("cues"):
        return existing

    pieces, cues, elapsed, rate = [], [], 0.0, 24000
    voices = assign_voices(unit_id, lines)
    prev_speaker = None
    for speaker, v, text in lines:
        audio = await synth(text, voices[speaker])
        seconds, rate = mp3_info(audio)
        if prev_speaker is not None:
            gap = silence_mp3(TURN_GAP, rate)
            pieces.append(gap)
            elapsed += mp3_info(gap)[0]
        cues.append({"t": round(elapsed, 2), "sp": speaker})
        pieces.append(audio)
        elapsed += seconds
        prev_speaker = speaker

    data = b"".join(pieces)
    with open(out_mp3, "wb") as fh:
        fh.write(data)
    return {"f": unit_id + ".mp3", "d": round(elapsed, 2), "cues": cues}


async def build_demo():
    """Muestra corta con las cuatro voces, para oirlas antes de grabar las 60
    unidades. Usa frases reales del material y el mismo reparto de voces que
    la grabacion de verdad, asi que lo que se oye aqui es lo que va a salir."""
    wanted = ["en-GB-SoniaNeural", "en-GB-RyanNeural",
              "en-GB-LibbyNeural", "en-GB-ThomasNeural"]
    chosen = {}
    for unit_id, lines in listening_units():
        voices = assign_voices(unit_id, lines)
        for speaker, v, text in lines:
            voice = voices[speaker]
            if voice in wanted and voice not in chosen and 12 <= len(text.split()) <= 38:
                chosen[voice] = (speaker, text)
        if len(chosen) == len(wanted):
            break

    if not os.path.isdir(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    pieces, rate = [], 24000
    print("Grabando una muestra con las cuatro voces...\n")
    for voice in wanted:
        if voice not in chosen:
            continue
        speaker, text = chosen[voice]
        print("  %-22s (%s)" % (voice.replace("en-GB-", "").replace("Neural", ""), speaker))
        print("    \"%s\"" % (text[:76] + ("..." if len(text) > 76 else "")))
        audio = await synth(text, voice)
        rate = mp3_info(audio)[1]
        if pieces:
            pieces.append(silence_mp3(0.8, rate))
        pieces.append(audio)

    out = os.path.join(AUDIO_DIR, "muestra-voces.mp3")
    with open(out, "wb") as fh:
        fh.write(b"".join(pieces))
    seconds = mp3_info(b"".join(pieces))[0]
    print("\nMuestra lista: %s  (%d segundos)" % (out, round(seconds)))
    print("Escuchala. Si te convence, graba las 60 unidades; si no, no has")
    print("perdido nada: este fichero no afecta a la aplicacion.")
    return 0


async def main_async(args):
    if args.list_voices:
        import edge_tts
        for v in await edge_tts.list_voices():
            if v["Locale"].startswith("en-GB") or v["Locale"].startswith("en-IE"):
                print("%-28s %-8s %s" % (v["ShortName"], v["Gender"], v["Locale"]))
        return 0

    if args.demo:
        return await build_demo()

    if not os.path.isdir(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    units = listening_units()
    if args.only:
        wanted = set(args.only)
        units = [u for u in units if u[0] in wanted]
        missing = wanted - set(u[0] for u in units)
        if missing:
            print("No existen estas unidades: %s" % ", ".join(sorted(missing)), file=sys.stderr)
            return 1

    manifest_path = os.path.join(AUDIO_DIR, "manifest.json")
    files = {}
    if os.path.exists(manifest_path):
        try:
            files = json.load(io.open(manifest_path, encoding="utf-8")).get("files", {})
        except ValueError:
            files = {}

    print("Grabando %d unidades de listening..." % len(units))
    for idx, (unit_id, lines) in enumerate(units, 1):
        words = sum(len(t.split()) for _, _, t in lines)
        print("  [%2d/%2d] %-22s %3d lineas · %4d palabras" %
              (idx, len(units), unit_id, len(lines), words), end="", flush=True)
        try:
            entry = await build_unit(unit_id, lines, args.force, files.get(unit_id))
            files[unit_id] = entry
            print("  ->  %.1f s" % entry["d"])
        except Exception as exc:                       # noqa: BLE001
            print("  ->  ERROR: %s" % exc)
            if args.stop_on_error:
                return 1

    with io.open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump({"version": 1, "files": files}, fh, ensure_ascii=False, indent=1)
    total = sum(f["d"] for f in files.values())
    print("\nListo: %d audios · %d min %02d s en total" %
          (len(files), int(total // 60), int(total % 60)))
    print("Manifest: %s" % manifest_path)
    print("Sube la carpeta audio/ junto con index.html y la aplicacion los usara sola.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Graba los audios de Listening con edge-tts.")
    ap.add_argument("--only", nargs="+", metavar="UNIDAD",
                    help="graba solo estas unidades (p. ej. listening_b1_t1)")
    ap.add_argument("--force", action="store_true", help="regraba aunque el fichero ya exista")
    ap.add_argument("--demo", action="store_true",
                    help="graba solo una muestra corta con las cuatro voces, para oirlas")
    ap.add_argument("--list-voices", action="store_true", help="muestra las voces britanicas disponibles")
    ap.add_argument("--stop-on-error", action="store_true", help="para en el primer fallo")
    args = ap.parse_args()
    try:
        import edge_tts                                # noqa: F401
    except ImportError:
        print("Falta edge-tts. Instalalo con:  pip install edge-tts", file=sys.stderr)
        return 1
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
