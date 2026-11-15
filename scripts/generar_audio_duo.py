#!/usr/bin/env python3
"""
generar_audio_duo.py

Sintetiza las locuciones de un guion por escenas alternando entre:
  - 'jose':   contenedor Docker `f5-tts` (voz clonada `jose`)
  - 'jarvis': contenedor Docker `kokoro-tts` (voz `em_alex`)

Ambos contenedores comparten el puerto host 8880, por lo que el script agrupa
las síntesis por locutor y gestiona la parada/arranque secuencial de Docker.
Genera `audio/manifest_audio.json` con la duración exacta de cada segmento.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import wave
import requests

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_DIR = os.path.join(PROJECT_DIR, "audio")
DEFAULT_SCRIPT = os.path.join(AUDIO_DIR, "guion_escenas.json")
PROTO_SCRIPT = os.path.join(AUDIO_DIR, "guion_prototipo_b3.json")
MANIFEST_FILE = os.path.join(AUDIO_DIR, "manifest_audio.json")
API_BASE = os.environ.get("TTS_BASE_URL", "http://localhost:8880")


def run_docker(args):
    return subprocess.run(["docker"] + args, capture_output=True, text=True)


def switch_tts_container(target_container: str, other_container: str, timeout: int = 90):
    """Detiene el contenedor opuesto y arranca el necesario en el puerto 8880."""
    print(f"\n[*] Cambiando motor TTS en puerto 8880 -> {target_container}")
    run_docker(["stop", other_container])

    inspect = run_docker(["inspect", "-f", "{{.State.Running}}", target_container])
    if inspect.returncode != 0:
        print(f"[!] Error: El contenedor '{target_container}' no existe en Docker.")
        sys.exit(1)

    if inspect.stdout.strip() != "true":
        res = run_docker(["start", target_container])
        if res.returncode != 0:
            print(f"[!] Error al arrancar {target_container}: {res.stderr}")
            sys.exit(1)

    deadline = time.time() + timeout
    endpoints = ["/v1/models", "/docs", "/health", "/"]
    while time.time() < deadline:
        for ep in endpoints:
            try:
                r = requests.get(f"{API_BASE}{ep}", timeout=2)
                if r.status_code == 200:
                    print(f"[✓] {target_container} operativo en {API_BASE} ({ep})")
                    return
            except requests.RequestException:
                pass
        time.sleep(2)

    print(f"[!] Timeout esperando a {target_container} en {API_BASE}")
    sys.exit(1)


def get_wav_duration(path: str) -> float:
    with wave.open(path, "rb") as wf:
        rate = wf.getframerate()
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        data = wf.readframes(-1)
        actual_frames = len(data) // (n_channels * sampwidth)
        return actual_frames / float(rate) if rate else 0.0


def synthesize_line(speaker: str, text: str, out_path: str, engine: str = "kokoro"):
    """Envía una petición OpenAI-compatible a /v1/audio/speech y normaliza la cabecera WAV."""
    if engine == "f5" and speaker == "jose":
        payload = {
            "model": "f5-tts",
            "input": text,
            "voice": "jose",
            "response_format": "wav",
            "speed": 1.0,
        }
    elif speaker == "jose":
        # Kokoro voz en español masculina (la misma que en democracia)
        payload = {
            "model": "kokoro",
            "input": text,
            "voice": os.environ.get("JOSE_VOICE", "em_alex"),
            "response_format": "wav",
        }
    else:
        # Jarvis voz en español alternativa (em_santa) o personalizada
        payload = {
            "model": "kokoro",
            "input": text,
            "voice": os.environ.get("JARVIS_VOICE", "em_santa"),
            "response_format": "wav",
        }

    resp = requests.post(f"{API_BASE}/v1/audio/speech", json=payload, timeout=300)
    if resp.status_code != 200:
        print(f"[!] Error HTTP {resp.status_code} sintetizando '{speaker}': {resp.text}")
        sys.exit(1)

    tmp_path = f"{out_path}.raw.wav"
    with open(tmp_path, "wb") as f:
        f.write(resp.content)

    # Normalizar cabecera RIFF/WAV (algunos endpoints streaming escriben tamaño 0xFFFFFFFF)
    fix = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", tmp_path, "-c:a", "pcm_s16le", out_path],
        capture_output=True,
        text=True,
    )
    if fix.returncode == 0 and os.path.exists(out_path):
        os.remove(tmp_path)
    else:
        os.replace(tmp_path, out_path)


def main():
    parser = argparse.ArgumentParser(description="Genera locuciones en dúo (Jose F5-TTS + Jarvis Kokoro).")
    parser.add_argument("--input", default=None, help="Ruta al guion JSON de escenas")
    parser.add_argument("--prototipo", action="store_true", help="Usa audio/guion_prototipo_b3.json")
    parser.add_argument("--manifest", default=MANIFEST_FILE, help="Ruta de salida del manifest JSON")
    parser.add_argument("--force", action="store_true", help="Regenera incluso si el archivo .wav ya existe")
    parser.add_argument("--engine", choices=["kokoro", "f5"], default="kokoro", help="Motor TTS para Jose (kokoro es estable y rápido; f5 usa GPU xpu)")
    args = parser.parse_args()

    script_path = args.input or (PROTO_SCRIPT if args.prototipo else DEFAULT_SCRIPT)
    if not os.path.exists(script_path):
        print(f"[!] No se encuentra el guion JSON: {script_path}")
        sys.exit(1)

    os.makedirs(AUDIO_DIR, exist_ok=True)
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenes = data["scenes"] if isinstance(data, dict) else data
    title = data.get("title", "Equilibristas de Golang") if isinstance(data, dict) else "Equilibristas de Golang"

    if args.engine == "kokoro":
        # Todo corre sobre kokoro-tts en CPU (em_alex para Jose, em_santa para Jarvis)
        switch_tts_container("kokoro-tts", "f5-tts")
        for s in scenes:
            speaker = s.get("speaker", "jose")
            wav_path = os.path.join(AUDIO_DIR, f"{s['id']}.wav")
            if args.force or not os.path.exists(wav_path):
                print(f"[+] [{speaker.upper()}] Generando {s['id']}.wav con Kokoro ({len(s['text'])} chars)...")
                synthesize_line(speaker, s["text"], wav_path, engine="kokoro")
                dur = get_wav_duration(wav_path)
                print(f"    ✓ Guardado ({dur:.2f}s): {wav_path}")
    else:
        # Modo mixto con f5-tts
        for speaker, container, other in [
            ("jose", "f5-tts", "kokoro-tts"),
            ("jarvis", "kokoro-tts", "f5-tts"),
        ]:
            pending = []
            for s in scenes:
                if s.get("speaker") != speaker:
                    continue
                wav_path = os.path.join(AUDIO_DIR, f"{s['id']}.wav")
                if args.force or not os.path.exists(wav_path):
                    pending.append((s, wav_path))

            if pending:
                switch_tts_container(container, other)
                for s, wav_path in pending:
                    print(f"[+] [{speaker.upper()}] Generando {s['id']}.wav ({len(s['text'])} chars)...")
                    synthesize_line(speaker, s["text"], wav_path, engine="f5")
                    dur = get_wav_duration(wav_path)
                    print(f"    ✓ Guardado ({dur:.2f}s): {wav_path}")

    # Construir manifest ordenado con marcas de tiempo exactas
    manifest_scenes = []
    cursor = 0.0
    for s in scenes:
        wav_rel = os.path.join("audio", f"{s['id']}.wav")
        wav_abs = os.path.join(PROJECT_DIR, wav_rel)
        if not os.path.exists(wav_abs):
            print(f"[!] Falta el audio esperado: {wav_abs}")
            sys.exit(1)
        dur = get_wav_duration(wav_abs)
        entry = {
            "id": s["id"],
            "speaker": s["speaker"],
            "layout": s.get("layout", "code"),
            "title": s.get("title", ""),
            "visual": s.get("visual", ""),
            "avatar_mode": s.get("avatar_mode", "full" if s.get("layout") in ("intro", "outro") else "crop512"),
            "audio": wav_rel,
            "duration_sec": round(dur, 3),
            "start_sec": round(cursor, 3),
            "end_sec": round(cursor + dur, 3),
        }
        manifest_scenes.append(entry)
        cursor += dur

    manifest = {
        "title": title,
        "total_duration_sec": round(cursor, 3),
        "scenes": manifest_scenes,
    }
    with open(args.manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Manifest generado: {args.manifest} (Duración total: {cursor:.2f}s)")


if __name__ == "__main__":
    main()

