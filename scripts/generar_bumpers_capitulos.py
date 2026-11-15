#!/usr/bin/env python3
"""
generar_bumpers_capitulos.py

Genera tarjetas separadoras (bumpers) de 3 segundos a 1920x1080 @ 25fps
con audio AAC para intercalar entre las partes del documental de 1 hora.
"""

import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BUMPERS_DIR = os.path.join(PROJECT_DIR, "clips", "bumpers")
os.makedirs(BUMPERS_DIR, exist_ok=True)

BUMPERS = [
    {
        "id": "bumper_01_parte1",
        "part": "PARTE 01 // CÓDIGO ARTESANAL",
        "title": "Cimientos y Concurrencia en Go",
        "subtitle": "Goroutines, Worker Pools, Tensores Manuales y Structs",
    },
    {
        "id": "bumper_02_parte2",
        "part": "PARTE 02 // ÁLGEBRA PROFESIONAL",
        "title": "El Dolor Manual y la Llegada de Gonum",
        "subtitle": "Escalado Matricial, BLAS y Aceleración en GPU Intel Arc",
    },
    {
        "id": "bumper_03_parte3",
        "part": "PARTE 03 // ENTRENAMIENTO",
        "title": "Anatomía Visual del Aprendizaje",
        "subtitle": "Bucle XOR, Backpropagation y la Geometría de Peso vs Sesgo",
    },
    {
        "id": "bumper_04_parte4",
        "part": "PARTE 04 // SIMULACIÓN 60 FPS",
        "title": "La Vida en Tiempo Real y el Manifold",
        "subtitle": "Simulador Ebiten, Deep Space Stretching y WebAssembly",
    },
    {
        "id": "bumper_05_parte5",
        "part": "PARTE 05 // SILICIO LIBRE",
        "title": "Del Cloud al Silicio Abierto RISC-V",
        "subtitle": "SoC Kendryte K230 (T-Head C908) y Ensamblador Vectorial RVV 1.0",
    },
]


def create_bumper_image(spec, out_png):
    img = Image.new("RGBA", (1920, 1080), (11, 15, 25, 255))
    draw = ImageDraw.Draw(img)

    # Rejilla sutil de fondo
    grid_color = (255, 255, 255, 8)
    for x in range(0, 1920, 80):
        draw.line([(x, 0), (x, 1080)], fill=grid_color, width=1)
    for y in range(0, 1080, 80):
        draw.line([(0, y), (1920, y)], fill=grid_color, width=1)

    # Marco central
    draw.rectangle([(160, 160), (1760, 920)], outline=(0, 122, 255, 60), width=2)
    draw.rectangle([(170, 170), (1750, 910)], outline=(255, 255, 255, 20), width=1)

    # Tipografías estándar
    try:
        font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
    except IOError:
        font_badge = font_title = font_sub = ImageFont.load_default()

    # Badge superior
    badge_text = spec["part"]
    draw.rounded_rectangle([(240, 310), (240 + len(badge_text) * 16 + 40, 365)], radius=6, fill=(0, 122, 255, 40), outline=(0, 122, 255, 180), width=1)
    draw.text((260, 322), badge_text, font=font_badge, fill=(0, 210, 255, 255))

    # Título principal
    draw.text((240, 420), spec["title"], font=font_title, fill=(240, 245, 255, 255))

    # Línea decorativa
    draw.line([(240, 520), (1000, 520)], fill=(0, 210, 255, 180), width=3)

    # Subtítulo explicativo
    draw.text((240, 560), spec["subtitle"], font=font_sub, fill=(160, 175, 200, 255))

    img.save(out_png)


def main():
    for spec in BUMPERS:
        png_path = os.path.join(BUMPERS_DIR, f"{spec['id']}.png")
        mp4_path = os.path.join(BUMPERS_DIR, f"{spec['id']}.mp4")
        create_bumper_image(spec, png_path)

        # Generar vídeo MP4 de 3 segundos @ 25fps con audio estéreo silente de 48kHz
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", png_path,
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-t", "3.0",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            mp4_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"[✓] Bumper generado: {mp4_path}")


if __name__ == "__main__":
    main()

