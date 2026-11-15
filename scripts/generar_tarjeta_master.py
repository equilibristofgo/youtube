#!/usr/bin/env python3
"""
generar_tarjeta_master.py

Genera la miniatura definitiva de alto impacto para el vídeo maestro de 1 hora:
"El Fin del Monopolio de NVIDIA y x86: Creamos una IA en Silicio Libre RISC-V con Go"
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_PATH = os.path.join(PROJECT_DIR, "tarjetas", "tarjeta_master_60min.png")
AVATAR_PATH = os.path.join(PROJECT_DIR, "presentador_podcast_avatar.jpg")

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def main():
    w, h = 1920, 1080
    im = Image.new("RGBA", (w, h), (10, 14, 20, 255))
    draw = ImageDraw.Draw(im)

    # 1. Fondo con degradado y cuadrícula sutil
    for y in range(h):
        r = int(8 + (y / h) * 12)
        g = int(12 + (y / h) * 16)
        b = int(24 + (y / h) * 35)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Rejilla cibernética sutil
    for x in range(0, w, 60):
        draw.line([(x, 0), (x, h)], fill=(30, 42, 60, 45), width=1)
    for y in range(0, h, 60):
        draw.line([(0, y), (w, y)], fill=(30, 42, 60, 45), width=1)

    # 2. Resplandor / Glow lateral cian y dorado
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([(-150, -150), (600, 600)], fill=(0, 173, 216, 50))
    gdraw.ellipse([(1400, 600), (2100, 1200)], fill=(255, 180, 0, 35))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    im = Image.alpha_composite(im, glow)
    draw = ImageDraw.Draw(im)

    # 3. Avatar del presentador en la derecha
    if os.path.exists(AVATAR_PATH):
        av = Image.open(AVATAR_PATH).convert("RGB")
        # Recorte de primer plano
        cw, ch = av.size
        crop_box = (int(cw * 0.28), int(ch * 0.05), int(cw * 0.76), int(ch * 0.95))
        av_cropped = av.crop(crop_box).resize((680, 850), Image.Resampling.LANCZOS)

        # Máscara elíptica / degradado en la base
        mask = Image.new("L", (680, 850), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.rounded_rectangle([(10, 10), (670, 840)], radius=40, fill=255)
        # Difuminado hacia la izquierda y abajo
        for i in range(120):
            mdraw.line([(0, 850 - i), (680, 850 - i)], fill=int(255 * (1 - i / 120)))

        # Borde brillante al contenedor del avatar
        av_x = 1180
        av_y = 140
        draw.rounded_rectangle([(av_x - 6, av_y - 6), (av_x + 686, av_y + 856)], radius=45, fill=(0, 173, 216, 120))
        draw.rounded_rectangle([(av_x - 2, av_y - 2), (av_x + 682, av_y + 852)], radius=42, fill=(15, 23, 36, 255))
        im.paste(av_cropped, (av_x, av_y), mask)

    # 4. Textos de Gancho en la columna izquierda
    # Banner superior: 1 HORA MASTERCLASS
    draw.rounded_rectangle([(80, 70), (560, 130)], radius=12, fill=(230, 57, 70, 255))
    draw.text((105, 82), "DOCUMENTAL // 1 HORA COMPLETA", font=font(FONT_MONO, 24), fill=(255, 255, 255, 255))

    draw.rounded_rectangle([(580, 70), (960, 130)], radius=12, fill=(0, 173, 216, 40), outline=(0, 173, 216, 200), width=2)
    draw.text((605, 82), "EQUILIBRISTAS DE GOLANG", font=font(FONT_MONO, 22), fill=(0, 215, 255, 255))

    # Título Principal Gigante
    draw.text((80, 160), "EL FIN DEL MONOPOLIO", font=font(FONT_BOLD, 74), fill=(255, 255, 255, 255))
    draw.text((80, 250), "DE NVIDIA Y x86", font=font(FONT_BOLD, 88), fill=(255, 230, 40, 255))

    # Barra separadora cian
    draw.line([(80, 365), (1100, 365)], fill=(0, 173, 216, 255), width=5)

    # Subtítulo explicativo
    draw.text((80, 395), "CREAMOS UNA INTELIGENCIA ARTIFICIAL", font=font(FONT_BOLD, 38), fill=(230, 240, 250, 255))
    draw.text((80, 445), "EN SILICIO LIBRE RISC-V CON GO", font=font(FONT_BOLD, 42), fill=(0, 210, 255, 255))

    # Caja de Temario / Capítulos clave
    draw.rounded_rectangle([(80, 520), (1100, 830)], radius=18, fill=(18, 25, 38, 240), outline=(45, 60, 85, 255), width=2)
    
    bullets = [
        ("01", "Cimientos & Tensores", "Goroutines, Worker Pools y Memoria Manual"),
        ("02", "El Salto a Gonum", "Álgebra Matricial Profesional y GPU Intel Arc"),
        ("03", "Anatomía del Aprendizaje", "XOR, Backpropagation y Visualización 2D"),
        ("04", "Simulador Ebiten 60 FPS", "Hipótesis del Manifold y WebAssembly"),
        ("05", "Kendryte K230 Edge AI", "Ensamblador Vectorial RVV 1.0 (VLA) en Go"),
    ]

    y_pos = 540
    for num, title_b, desc_b in bullets:
        draw.rounded_rectangle([(105, y_pos), (155, y_pos + 42)], radius=8, fill=(0, 173, 216, 220))
        draw.text((114, y_pos + 8), num, font=font(FONT_MONO, 22), fill=(10, 15, 25, 255))
        draw.text((175, y_pos + 6), title_b, font=font(FONT_BOLD, 24), fill=(255, 255, 255, 255))
        draw.text((540, y_pos + 8), f"— {desc_b}", font=font(FONT_SANS, 20), fill=(160, 175, 195, 255))
        y_pos += 56

    # Badges inferiores de tecnología
    badges = [
        ("100% GOLANG", (0, 173, 216, 255), (10, 25, 35, 255)),
        ("RISC-V RVV 1.0", (255, 190, 0, 255), (35, 25, 5, 255)),
        ("CANMV-K230", (50, 205, 50, 255), (10, 30, 10, 255)),
        ("SIN PYTHON / CUDA", (230, 60, 60, 255), (35, 10, 10, 255)),
        ("EBITEN 60 FPS", (180, 100, 255, 255), (25, 10, 35, 255)),
    ]

    bx = 80
    for text_b, bg_b, fg_b in badges:
        bw = len(text_b) * 16 + 32
        draw.rounded_rectangle([(bx, 865), (bx + bw, 925)], radius=12, fill=bg_b)
        draw.text((bx + 16, 882), text_b, font=font(FONT_MONO, 22), fill=fg_b)
        bx += bw + 20

    # Etiqueta de duración "1h 02m" estilo YouTube
    draw.rounded_rectangle([(1630, 930), (1850, 1010)], radius=14, fill=(0, 0, 0, 220), outline=(255, 230, 40, 255), width=2)
    draw.text((1650, 946), "⏱ 01:02:30", font=font(FONT_BOLD, 34), fill=(255, 230, 40, 255))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    im.save(OUT_PATH, format="PNG")
    print(f"[✓] Miniatura del Máster generada en: {OUT_PATH}")


if __name__ == "__main__":
    main()
