#!/usr/bin/env python3
"""
montar_video_master_60min.py

Concatena los 5 episodios, los bumpers de transición y el prólogo Star Wars
en el documental maestro de 1 hora.
Calcula e imprime los timestamps exactos para la descripción de YouTube.
"""

import json
import os
import subprocess
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
MASTER_OUTPUT = os.path.join(OUTPUT_DIR, "video_master_60min_deep_learning_riscv_go.mp4")

TIMELINE = [
    {"name": "Prólogo Galáctico: La Rebelión del Silicio Libre", "path": "clips/prologo_star_wars_crawl_audio.mp4"},
    {"name": "Separador Parte 1", "path": "clips/bumpers/bumper_01_parte1.mp4", "is_bumper": True},
    {"name": "PARTE 1: Cimientos y Concurrencia (Goroutines y Tensores Manuales)", "path": "downloads/video1_normalized_1080p.mp4"},
    {"name": "Separador Parte 2", "path": "clips/bumpers/bumper_02_parte2.mp4", "is_bumper": True},
    {"name": "PARTE 2: El Dolor del Escalado y Gonum (Álgebra y GPU Intel Arc)", "path": "downloads/video2_normalized_1080p.mp4"},
    {"name": "Separador Parte 3", "path": "clips/bumpers/bumper_03_parte3.mp4", "is_bumper": True},
    {"name": "PARTE 3: Anatomía Visual del Aprendizaje (XOR, Backpropagation y Sesgo)", "path": "output/video3_anatomia_aprendizaje_go.mp4"},
    {"name": "Separador Parte 4", "path": "clips/bumpers/bumper_04_parte4.mp4", "is_bumper": True},
    {"name": "PARTE 4: La Vida en Tiempo Real a 60 FPS (Ebiten, Manifold y WASM)", "path": "output/video4_tejido_neuronal_ebiten.mp4"},
    {"name": "Separador Parte 5", "path": "clips/bumpers/bumper_05_parte5.mp4", "is_bumper": True},
    {"name": "PARTE 5: Del Cloud al Silicio Libre (Kendryte K230 y Ensamblador RVV 1.0)", "path": "output/video5_silicio_libre_riscv.mp4"},
]


def get_duration(abs_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        abs_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def main():
    dry_run = "--dry-run" in sys.argv
    concat_list_path = os.path.join(OUTPUT_DIR, "concat_master.txt")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=== Comprobando duraciones y generando Timestamps del Máster ===")
    current_time = 0.0
    timestamps_text = []

    with open(concat_list_path, "w", encoding="utf-8") as f_concat:
        for item in TIMELINE:
            abs_path = os.path.join(PROJECT_DIR, item["path"])
            if not os.path.exists(abs_path):
                if dry_run and "video5" in item["path"]:
                    # Duración estimada del manifest de video 5
                    dur = 673.0
                    print(f"  [~] Estimando duración para {item['name']} (pendiente de render): {dur:.1f}s")
                else:
                    print(f"[!] Falta archivo necesario para el máster: {abs_path}")
                    sys.exit(1)
            else:
                dur = get_duration(abs_path)

            if not item.get("is_bumper"):
                ts = format_timestamp(current_time)
                line = f"{ts} - {item['name']}"
                timestamps_text.append(line)
                print(f"  [{ts}] {item['name']} ({dur:.1f}s)")
            else:
                print(f"  [--:--] {item['name']} ({dur:.1f}s)")

            f_concat.write(f"file '{abs_path}'\n")
            current_time += dur

    total_fmt = format_timestamp(current_time)
    print(f"\n[✓] Duración total estimada: {total_fmt} ({current_time:.2f}s)")

    print("\n--- TIMESTAMPS PARA LA DESCRIPCIÓN DE YOUTUBE ---")
    print("\n".join(timestamps_text))
    print("--------------------------------------------------\n")

    if dry_run:
        print("[*] Modo --dry-run activado: No se ejecuta la concatenación final hasta que esté listo Video 5.")
        return

    print(f"[*] Concatenando en {MASTER_OUTPUT} con ffmpeg concat demuxer (stream copy)...")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        MASTER_OUTPUT
    ]
    res = subprocess.run(cmd)
    if res.returncode == 0 and os.path.exists(MASTER_OUTPUT):
        print(f"\n[✓] ¡VÍDEO MAESTRO GENERADO CON ÉXITO!")
        print(f"    Ruta: {MASTER_OUTPUT}")
        print(f"    Tamaño: {os.path.getsize(MASTER_OUTPUT) / (1024*1024):.1f} MB")
    else:
        print("[!] Error en la concatenación con ffmpeg.")
        sys.exit(1)


if __name__ == "__main__":
    main()

