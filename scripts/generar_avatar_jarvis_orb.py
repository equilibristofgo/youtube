#!/usr/bin/env python3
"""
generar_avatar_jarvis_orb.py

Renderizador offline en CPU (Pillow + NumPy + FFmpeg) del Orbe holográfico de Jarvis,
portado de `JarvisOrbVisualizer` (`13_livekit_agent/src/agent_vision.py`).
Modula el radio del núcleo y las ondas concéntricas con la envolvente RMS real del `.wav`.
"""

import argparse
import json
import math
import os
import subprocess
import sys
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_MANIFEST = os.path.join(PROJECT_DIR, "audio", "manifest_audio.json")
CLIPS_DIR = os.path.join(PROJECT_DIR, "clips")
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def load_font(size: int):
    try:
        return ImageFont.truetype(FONT_BOLD, size)
    except Exception:
        return ImageFont.load_default()


def compute_rms_envelope(wav_path: str, fps: int):
    """Devuelve (duration_sec, array_rms_normalizado_por_frame)."""
    with wave.open(wav_path, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        raw = wf.readframes(-1)

    if sampwidth == 2:
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        samples = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    elif sampwidth == 1:
        samples = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        raise ValueError(f"Ancho de muestra no soportado: {sampwidth} bytes")

    if n_channels > 1:
        samples = samples.reshape(-1, n_channels).mean(axis=1)

    duration = len(samples) / float(framerate) if framerate else 0.0

    total_video_frames = max(1, int(math.ceil(duration * fps)))
    samples_per_frame = max(1, int(framerate / fps))

    rms_vals = np.zeros(total_video_frames, dtype=np.float32)
    for idx in range(total_video_frames):
        start = int(idx * framerate / fps)
        end = min(len(samples), start + samples_per_frame)
        if end > start:
            chunk = samples[start:end]
            rms_vals[idx] = float(np.sqrt(np.mean(chunk * chunk)))

    peak = float(np.percentile(rms_vals, 98)) if len(rms_vals) > 0 else 1.0
    if peak > 1e-5:
        rms_vals = np.clip(rms_vals / peak, 0.0, 1.35)
    return duration, rms_vals


def draw_orb_frame(width: int, height: int, t: float, amp: float, font_badge) -> bytes:
    """Dibuja un fotograma del orbe reactivo y devuelve bytes RGBA."""
    img = Image.new("RGBA", (width, height), (10, 14, 23, 255))
    draw = ImageDraw.Draw(img)

    cx, cy = width // 2, int(height * 0.53)
    scale = min(width, height) / 512.0

    # Rejilla sutil tecnológica de fondo
    step = int(48 * scale)
    for x in range(0, width, max(16, step)):
        draw.line([(x, 0), (x, height)], fill=(18, 28, 44, 160), width=1)
    for y in range(0, height, max(16, step)):
        draw.line([(0, y), (width, y)], fill=(18, 28, 44, 160), width=1)

    # Anillos orbitales giratorios (efecto thinking/procesando continuo sutil)
    for r_x, r_y, speed in [(150, 52, 2.8), (128, 42, -3.4)]:
        angle = t * speed
        rx = r_x * scale * (1.0 + 0.08 * amp)
        ry = r_y * scale * (1.0 + 0.08 * amp)
        for dot in range(12):
            th = angle + dot * (math.pi / 6.0)
            dx = cx + rx * math.cos(th)
            dy = cy + ry * math.sin(th)
            r_dot = max(2, int(3.5 * scale))
            draw.ellipse([dx - r_dot, dy - r_dot, dx + r_dot, dy + r_dot], fill=(0, 240, 255, 165))

    # Ondas sonoras concéntricas reactivas al audio
    base_r = (68.0 + amp * 34.0 + math.sin(t * 3.0) * 3.0) * scale
    for i in range(1, 4):
        ring_r = base_r + (i * 26.0 * scale) + amp * (i * 10.0 * scale)
        alpha = max(25, int(190 - i * 48))
        draw.ellipse(
            [cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
            outline=(0, 230, 255, alpha),
            width=max(2, int(3 * scale)),
        )

    # Núcleo holográfico principal
    draw.ellipse(
        [cx - base_r, cy - base_r, cx + base_r, cy + base_r],
        fill=(0, 145, 240, 230),
        outline=(195, 248, 255, 255),
        width=max(2, int(4 * scale)),
    )
    inner_r = (20.0 + amp * 12.0) * scale
    draw.ellipse(
        [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
        fill=(235, 252, 255, 255),
    )

    # Etiqueta superior estilo HUD
    pad_x = int(14 * scale)
    pad_y = int(12 * scale)
    box_h = int(34 * scale)
    draw.rounded_rectangle(
        [pad_x, pad_y, width - pad_x, pad_y + box_h],
        radius=max(4, int(8 * scale)),
        fill=(15, 26, 42, 230),
        outline=(0, 215, 255, 200),
        width=2,
    )
    label = "JARVIS // AI COPILOT [QWEN + KOKORO]"
    draw.text((pad_x + int(12 * scale), pad_y + int(8 * scale)), label, font=font_badge, fill=(140, 245, 255, 255))

    # Barra inferior de estado / nivel RMS
    bar_y = height - int(22 * scale)
    draw.rectangle([pad_x, bar_y, width - pad_x, bar_y + int(8 * scale)], fill=(20, 32, 48, 255))
    active_w = int((width - 2 * pad_x) * min(1.0, 0.12 + amp * 0.85))
    draw.rectangle([pad_x, bar_y, pad_x + active_w, bar_y + int(8 * scale)], fill=(0, 230, 255, 255))

    return img.tobytes()


def render_orb_video(audio_path: str, output_path: str, fps: int, size: int, mode: str):
    if not os.path.exists(audio_path):
        print(f"[!] No se encuentra el audio: {audio_path}")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    width, height = (1920, 1080) if mode == "full" else (size, size)
    font_size = 24 if mode == "full" else max(13, int(17 * (size / 512.0)))
    font_badge = load_font(font_size)

    duration, rms_vals = compute_rms_envelope(audio_path, fps)
    total_frames = len(rms_vals)
    print(f"[*] Renderizando Orbe Jarvis ({width}x{height} @ {fps}fps, {total_frames} frames, {duration:.2f}s) -> {os.path.basename(output_path)}")

    ffmpeg_cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "rgba",
        "-s", f"{width}x{height}",
        "-r", str(fps),
        "-i", "-",
        "-i", os.path.abspath(audio_path),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        os.path.abspath(output_path),
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    smoothed_amp = 0.0
    dt = 1.0 / fps

    try:
        for i in range(total_frames):
            raw_amp = float(rms_vals[i])
            smoothed_amp = 0.55 * smoothed_amp + 0.45 * raw_amp
            frame_bytes = draw_orb_frame(width, height, i * dt, smoothed_amp, font_badge)
            proc.stdin.write(frame_bytes)
    finally:
        if proc.stdin:
            proc.stdin.close()
        ret = proc.wait()

    if ret != 0:
        print(f"[!] Error en FFmpeg codificando {output_path} (código {ret})")
        sys.exit(ret)

    print(f"[✓] Vídeo Orbe Jarvis generado: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Genera un MP4 del Orbe de Jarvis sincronizado con un archivo WAV.")
    parser.add_argument("--audio", default=None, help="Ruta al archivo de audio .wav de Jarvis")
    parser.add_argument("--output", default=None, help="Ruta del archivo .mp4 resultante")
    parser.add_argument("--fps", type=int, default=25, help="Fotogramas por segundo (por defecto 25)")
    parser.add_argument("--size", type=int, default=512, help="Tamaño cuadrado para modo pip (por defecto 512)")
    parser.add_argument("--mode", default="pip", choices=["pip", "full"], help="pip (cuadrado) o full (1920x1080)")
    parser.add_argument("--from-manifest", action="store_true", help="Procesa todas las escenas de Jarvis del manifest")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Ruta al manifest_audio.json")
    parser.add_argument("--force", action="store_true", help="Regenera clips existentes")
    args = parser.parse_args()

    if args.from_manifest:
        if not os.path.exists(args.manifest):
            print(f"[!] No se encuentra manifest: {args.manifest}")
            sys.exit(1)
        with open(args.manifest, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        for scene in manifest.get("scenes", []):
            if scene.get("speaker") != "jarvis":
                continue
            sc_id = scene["id"]
            audio_abs = os.path.join(PROJECT_DIR, scene["audio"])
            out_path = os.path.join(CLIPS_DIR, f"jarvis_{sc_id}.mp4")
            if not args.force and os.path.exists(out_path):
                print(f"[=] Saltando clip existente: {out_path}")
                continue
            mode = "full" if scene.get("layout") in ("intro", "outro") or not scene.get("visual") else "pip"
            render_orb_video(audio_abs, out_path, args.fps, args.size, mode)
    else:
        if not args.audio or not args.output:
            print("[!] Especifica --audio y --output, o usa --from-manifest.")
            sys.exit(1)
        render_orb_video(args.audio, args.output, args.fps, args.size, args.mode)


if __name__ == "__main__":
    main()
