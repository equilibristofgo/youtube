#!/usr/bin/env python3
"""
generar_tarjetas_codigo.py

Genera tarjetas visuales 1920x1080 estilo IDE oscuro ("Equilibristas de Golang")
para montaje híbrido con PiP en Blender VSE:
  - Columna izquierda (x=60..1120): código fuente real extraído de 14_nyu_00 con
    resaltado léxico y banda de foco/zoom en las líneas clave.
  - Columna derecha superior (x=1150..1860, y=145..630): gráfica PNG de gonum/plot
    o salida de terminal `$ go run main.go`.
  - Columna derecha inferior izquierda (x=1150..1475, y=650..1040): caja "CONCEPTO CLAVE".
  - Esquina inferior derecha (x=1492..1860, y=650..1040): marco "LIVE CAM // HOST & JARVIS"
    reservado para que Blender VSE incruste el PiP cuadrado (centro=1675,860, 350x350).
"""

import argparse
import os
import re
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SANDBOX_NYU_DIR = os.environ.get(
    "SANDBOX_NYU_DIR",
    "/home/jose/workspace/equilibristofgo/sandbox/14_nyu_00",
)
OUT_DIR = os.path.join(PROJECT_DIR, "tarjetas")

FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

GO_KEYWORDS = {
    "package", "import", "func", "for", "if", "else", "return", "var",
    "const", "type", "struct", "interface", "range", "go", "chan", "select",
    "defer", "switch", "case", "default", "TEXT", "RET", "JMP", "BNE",
    "MOVD", "VSETVLI", "VLE32", "VADDVV", "VSE32", "VFMACCVV", "SLLI", "ADD", "SUB",
}
GO_TYPES = {
    "float64", "float32", "int", "int64", "uint32", "string", "bool",
    "make", "len", "cap", "panic", "fmt", "math", "mat", "plot", "plotter",
    "Dense", "Neuron", "Layer", "NOSPLIT", "SB", "FP", "ZERO",
}

COLOR_BG = (13, 17, 23, 255)
COLOR_PANEL = (22, 27, 34, 245)
COLOR_PANEL_HDR = (30, 36, 46, 255)
COLOR_BORDER = (48, 54, 61, 255)
COLOR_CYAN = (0, 173, 216, 255)  # Go Gopher Cyan
COLOR_TEXT = (230, 237, 243, 255)
COLOR_MUTED = (139, 148, 158, 255)


def load_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def tokenize_code_line(line: str):
    """Tokenizador ligero para colorear Go y ensamblador Go/RISC-V."""
    stripped = line.lstrip()
    if stripped.startswith("//"):
        return [(line, (139, 148, 158, 255))]

    # Separar comentario al final si no está dentro de comillas simples
    code_part = line
    comment_part = ""
    in_str = False
    for idx, ch in enumerate(line):
        if ch == '"' and (idx == 0 or line[idx - 1] != "\\"):
            in_str = not in_str
        elif not in_str and line[idx : idx + 2] == "//":
            code_part = line[:idx]
            comment_part = line[idx:]
            break

    tokens = []
    pattern = re.compile(
        r'(".*?"|\b0x[0-9A-Fa-f]+\b|\b[A-Za-z_][A-Za-z0-9_]*\b|\b\d+(?:\.\d+)?\b|\s+|[^\sA-Za-z0-9_"]+|.)'
    )
    for tok in pattern.findall(code_part):
        if tok.startswith('"'):
            tokens.append((tok, (165, 214, 255, 255)))
        elif tok in GO_KEYWORDS:
            tokens.append((tok, (255, 123, 114, 255)))
        elif tok in GO_TYPES:
            tokens.append((tok, (255, 166, 87, 255)))
        elif re.match(r"^(?:0x[0-9A-Fa-f]+|\d+(?:\.\d+)?)$", tok):
            tokens.append((tok, (121, 192, 255, 255)))
        else:
            tokens.append((tok, COLOR_TEXT))

    if comment_part:
        tokens.append((comment_part, (139, 148, 158, 255)))
    return tokens


def read_code_slice(rel_path: str, start_line: int, end_line: int):
    full_path = os.path.join(SANDBOX_NYU_DIR, rel_path)
    if not os.path.exists(full_path):
        return None
    with open(full_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    s = max(1, start_line)
    e = min(len(lines), end_line)
    return [(ln, lines[ln - 1].replace("\t", "    ")) for ln in range(s, e + 1)]


def wrap_text_lines(text: str, max_chars: int):
    words = text.split()
    out, cur = [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if len(cand) <= max_chars:
            cur = cand
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def render_card(spec: dict):
    rel_file = spec["source_file"]
    code_lines = read_code_slice(rel_file, spec["line_start"], spec["line_end"])
    if code_lines is None:
        print(f"[!] Aviso: No se encontró {rel_file} en {SANDBOX_NYU_DIR}; saltando {spec['output']}.")
        return False

    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), COLOR_BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # Rejilla sutil
    for x in range(0, W, 64):
        draw.line([(x, 0), (x, H)], fill=(22, 29, 40, 255), width=1)
    for y in range(0, H, 64):
        draw.line([(0, y), (W, y)], fill=(22, 29, 40, 255), width=1)

    accent = spec.get("accent", COLOR_CYAN)
    draw.rectangle([0, 0, W, 6], fill=accent)

    # Cabecera
    f_badge = load_font(FONT_MONO_BOLD, 18)
    f_title = load_font(FONT_SANS_BOLD, 38)
    f_path = load_font(FONT_MONO, 19)

    badge_txt = spec["badge"]
    badge_w = max(360, len(badge_txt) * 12 + 40)
    draw.rounded_rectangle([60, 24, 60 + badge_w, 60], radius=8, fill=(14, 38, 52, 255), outline=accent, width=2)
    draw.text((78, 32), badge_txt, font=f_badge, fill=(140, 245, 255, 255))

    draw.text((60, 74), spec["title"], font=f_title, fill=COLOR_TEXT)

    path_txt = f"14_nyu_00/{rel_file}"
    draw.rounded_rectangle([1260, 24, 1860, 60], radius=8, fill=COLOR_PANEL, outline=COLOR_BORDER, width=2)
    draw.text((1280, 32), path_txt, font=f_path, fill=(121, 192, 255, 255))

    # --- COLUMNA IZQUIERDA: VENTANA DE CÓDIGO (x=60..1120, y=145..1040) ---
    draw.rounded_rectangle([60, 145, 1120, 1040], radius=14, fill=COLOR_PANEL, outline=COLOR_BORDER, width=2)
    draw.rounded_rectangle([60, 145, 1120, 188], radius=14, fill=COLOR_PANEL_HDR, outline=COLOR_BORDER, width=2)
    for idx, dot_col in enumerate([(248, 81, 73, 255), (227, 179, 65, 255), (63, 185, 80, 255)]):
        cx = 86 + idx * 24
        draw.ellipse([cx - 7, 160, cx + 7, 174], fill=dot_col)
    draw.text((168, 156), f"{os.path.basename(rel_file)}  [L{spec['line_start']}-L{spec['line_end']}]", font=f_path, fill=COLOR_MUTED)

    num_lines = len(code_lines)
    code_font_size = 18 if num_lines <= 32 else 16
    line_h = 25 if num_lines <= 32 else 22
    f_code = load_font(FONT_MONO, code_font_size)
    f_lnum = load_font(FONT_MONO, code_font_size - 1)

    focus_start, focus_end = spec.get("focus_lines", (0, 0))
    cur_y = 204
    max_code_chars = 85 if code_font_size == 18 else 94
    for ln, raw_line in code_lines:
        if cur_y + line_h > 1028:
            break
        if focus_start <= ln <= focus_end:
            draw.rectangle([64, cur_y - 2, 1116, cur_y + line_h - 3], fill=(18, 46, 64, 255))
            draw.rectangle([64, cur_y - 2, 70, cur_y + line_h - 3], fill=accent)

        draw.text((78, cur_y), f"{ln:3d}", font=f_lnum, fill=(110, 118, 129, 255))
        x_cursor = 128
        disp_line = raw_line[:max_code_chars] + ("…" if len(raw_line) > max_code_chars else "")
        for tok, col in tokenize_code_line(disp_line):
            draw.text((x_cursor, cur_y), tok, font=f_code, fill=col)
            bbox = draw.textbbox((x_cursor, cur_y), tok, font=f_code)
            x_cursor = bbox[2]
        cur_y += line_h

    # --- COLUMNA DERECHA SUPERIOR: GRÁFICA PNG O TERMINAL (x=1150..1860, y=145..630) ---
    draw.rounded_rectangle([1150, 145, 1860, 630], radius=14, fill=COLOR_PANEL, outline=COLOR_BORDER, width=2)
    draw.rounded_rectangle([1150, 145, 1860, 188], radius=14, fill=COLOR_PANEL_HDR, outline=COLOR_BORDER, width=2)
    draw.text((1175, 156), spec.get("right_header", "TERMINAL // go run main.go"), font=f_path, fill=(63, 185, 80, 255))

    right_img_rel = spec.get("right_image")
    if right_img_rel and os.path.exists(os.path.join(SANDBOX_NYU_DIR, right_img_rel)):
        plot_path = os.path.join(SANDBOX_NYU_DIR, right_img_rel)
        plot_img = Image.open(plot_path).convert("RGBA")
        avail_w, avail_h = 686, 418
        ratio = min(avail_w / plot_img.width, avail_h / plot_img.height)
        nw, nh = int(plot_img.width * ratio), int(plot_img.height * ratio)
        plot_resized = plot_img.resize((nw, nh), Image.Resampling.LANCZOS)
        px = 1150 + (710 - nw) // 2
        py = 192 + (434 - nh) // 2
        img.paste(plot_resized, (px, py), plot_resized)
    else:
        f_term = load_font(FONT_MONO, 17)
        ty = 205
        for tline in spec.get("terminal_lines", []):
            if ty > 605:
                break
            col = (63, 185, 80, 255) if tline.startswith("$") else (121, 192, 255, 255) if "->" in tline else COLOR_TEXT
            draw.text((1174, ty), tline[:62], font=f_term, fill=col)
            ty += 25

    # --- COLUMNA DERECHA INFERIOR IZQUIERDA: CONCEPTO CLAVE (x=1150..1475, y=650..1040) ---
    draw.rounded_rectangle([1150, 650, 1475, 1040], radius=14, fill=COLOR_PANEL, outline=accent, width=2)
    draw.rounded_rectangle([1150, 650, 1475, 688], radius=14, fill=(14, 38, 52, 255), outline=accent, width=2)
    f_note_hdr = load_font(FONT_MONO_BOLD, 16)
    f_note_body = load_font(FONT_SANS, 19)
    draw.text((1168, 660), "CONCEPTO CLAVE", font=f_note_hdr, fill=(140, 245, 255, 255))

    ny = 708
    for para in spec.get("key_points", []):
        for wline in wrap_text_lines(para, 29):
            if ny > 1010:
                break
            draw.text((1168, ny), wline, font=f_note_body, fill=COLOR_TEXT)
            ny += 25
        ny += 10

    # --- ESQUINA INFERIOR DERECHA: MARCO PIP (x=1492..1860, y=650..1040) ---
    # Centro exacto del viewport interior: (1675, 860), espacio útil 350x350
    draw.rounded_rectangle([1492, 650, 1860, 1040], radius=14, fill=(10, 14, 23, 255), outline=accent, width=2)
    draw.rounded_rectangle([1492, 650, 1860, 682], radius=14, fill=(14, 38, 52, 255), outline=accent, width=2)
    draw.text((1512, 658), "LIVE CAM // HOST & JARVIS", font=f_note_hdr, fill=(140, 245, 255, 255))

    out_path = os.path.join(OUT_DIR, spec["output"])
    os.makedirs(OUT_DIR, exist_ok=True)
    img.save(out_path, "PNG")
    print(f"[✓] Tarjeta generada: {out_path}")
    return True


CARD_SPECS = [
    # --- BLOQUE 3 (Prototipo + Serie) ---
    {
        "output": "tarjeta_b3_01_train_xor.png",
        "badge": "BLOQUE 3 // ANATOMÍA VISUAL DEL APRENDIZAJE",
        "title": "07-train: Backpropagation y XOR con Gonum",
        "source_file": "07-train/main.go",
        "line_start": 43,
        "line_end": 74,
        "focus_lines": (55, 72),
        "right_header": "TERMINAL // $ go run 07-train/main.go",
        "terminal_lines": [
            "$ cd 14_nyu_00/07-train && go run main.go",
            "Epoch 0    - Error sum: -0.9412",
            "Epoch 2000 - Error sum:  0.0314",
            "Epoch 4000 - Error sum:  0.0087",
            "Epoch 6000 - Error sum:  0.0041",
            "Epoch 8000 - Error sum:  0.0025",
            "",
            "Predicciones finales tras entrenamiento:",
            "Input: [0, 0] -> Target: 0 | Pred: 0.0231",
            "Input: [0, 1] -> Target: 1 | Pred: 0.9784",
            "Input: [1, 0] -> Target: 1 | Pred: 0.9791",
            "Input: [1, 1] -> Target: 0 | Pred: 0.0218",
        ],
        "key_points": [
            "• Forward: multiplica entradas x pesos y aplica sigmoide.",
            "• Backprop: propaga la 'culpa' hacia atrás con s*(1-s).",
            "• En 10.000 épocas resuelve XOR sin magia negra.",
        ],
    },
    {
        "output": "tarjeta_b3_02_sigmoid_plot.png",
        "badge": "BLOQUE 3 // FUNCIÓN DE ACTIVACIÓN",
        "title": "09-sigmoid-graph: La Rampa en 'S' con gonum/plot",
        "source_file": "09-sigmoid-graph/main.go",
        "line_start": 10,
        "line_end": 44,
        "focus_lines": (10, 12),
        "right_header": "OUTPUT // 09-sigmoid-graph/sigmoid.png",
        "right_image": "09-sigmoid-graph/sigmoid.png",
        "key_points": [
            "• Sigmoid(x) = 1 / (1 + e^-x).",
            "• Estruja cualquier número real entre 0 y 1.",
            "• Cuidado en redes profundas: la derivada se aplana en los extremos (Vanishing Gradient).",
        ],
    },
    {
        "output": "tarjeta_b3_03_bias_temp.png",
        "badge": "BLOQUE 3 // EL PODER DEL SESGO (BIAS)",
        "title": "10-neuron-temperatura: Desplazando el Umbral",
        "source_file": "10-neuron-temperatura/main.go",
        "line_start": 25,
        "line_end": 58,
        "focus_lines": (28, 35),
        "right_header": "OUTPUT // temperature_prediction.png",
        "right_image": "10-neuron-temperatura/temperature_prediction.png",
        "key_points": [
            "• El peso (W) inclina la pendiente de la curva.",
            "• El sesgo (b) desplaza el punto de activación en el tiempo.",
            "• Mismo peso (0.1), distinto bias (0.0 vs 0.5) = curvas desplazadas.",
        ],
    },
    {
        "output": "tarjeta_b3_04_jarvis_qa.png",
        "badge": "BLOQUE 3 // DUDAS & PREGUNTAS CON JARVIS",
        "title": "Sigmoide vs ReLU y el Sentido Intuitivo del Bias",
        "source_file": "10-neuron/main.go",
        "line_start": 55,
        "line_end": 85,
        "focus_lines": (62, 66),
        "right_header": "OUTPUT // sigmoid_vs_neuron.png",
        "right_image": "10-neuron/sigmoid_vs_neuron.png",
        "key_points": [
            "1. ¿Por qué cayó en desuso la Sigmoide en capas profundas?",
            "2. ¿Cómo explicar el sesgo (bias) sin fórmulas?",
            "-> Pregunta en directo al copiloto local.",
        ],
    },
    # --- BLOQUE 4 (Ebiten & Manifolds) ---
    {
        "output": "tarjeta_b4_01_ebiten_xor.png",
        "badge": "BLOQUE 4 // TIEMPO REAL A 60 FPS",
        "title": "10-neuron-js-golang: Simulador Interactivo en Ebiten",
        "source_file": "10-neuron-js-golang/main.go",
        "line_start": 1,
        "line_end": 32,
        "focus_lines": (1, 32),
        "right_header": "CONTROLES EN VIVO // Ebiten 60 FPS",
        "terminal_lines": [
            "$ cd 14_nyu_00/10-neuron-js-golang && go run main.go",
            "",
            "• Nodos: alpha proporcional a la activación.",
            "• Sinapsis: verde (+) / rojo (-) y grosor = |peso|.",
            "• Flecha ARRIBA: entrena XOR en tiempo real.",
            "• Flecha ABAJO : desentrena los pesos.",
            "• IZQ / DER    : ajusta el Learning Rate.",
        ],
        "key_points": [
            "• Adiós PNG estáticos: loop Update/Draw a 60 FPS.",
            "• Visualiza cómo los pesos cambian de signo al converger.",
        ],
    },
    {
        "output": "tarjeta_b4_02_manifold_space.png",
        "badge": "BLOQUE 4 // DEEP SPACE STRETCHING",
        "title": "11-juego-final: El Tejido Neuronal y la Hipótesis del Manifold",
        "source_file": "11-juego-final/main.go",
        "line_start": 1528,
        "line_end": 1560,
        "focus_lines": (1530, 1555),
        "right_header": "SIMULADOR EN VIVO // Controles y Estado",
        "terminal_lines": [
            "$ cd 14_nyu_00/11-juego-final && go run .",
            "",
            "• Tecla T: activa el auto-entrenamiento de la red.",
            "• Tecla S: simula el estiramiento del espacio cósmico.",
            "• Tecla V: activa el flujo de vectores y tensión.",
            "• Tecla X: conmuta el motor (Parallel / AVX / Level0).",
            "• P / M  : ajusta la velocidad de simulación.",
        ],
        "key_points": [
            "• La red dobla la cuadrícula 2D (\"la manta\") para separar estrellas.",
            "• Pizarra de cálculo con inspección tensorial en tiempo real.",
        ],
    },
    {
        "output": "tarjeta_b4_03_engines_matrix.png",
        "badge": "BLOQUE 4 // MULTIPLEXACIÓN DE MOTORES",
        "title": "nn/: De CPU y GPU Intel Arc a WebAssembly (WASM)",
        "source_file": "11-juego-final/js_bridge.go",
        "line_start": 1,
        "line_end": 33,
        "focus_lines": (12, 33),
        "right_header": "BACKENDS COMPILADOS // Go Cross-Platform",
        "terminal_lines": [
            "$ GOOS=js GOARCH=wasm go build -o web/game.wasm .",
            "",
            "Motores disponibles en tiempo real:",
            "  • standard : Go secuencial en CPU.",
            "  • parallel : Goroutines multinúcleo sincronizadas.",
            "  • avx      : Ensamblador vectorial SIMD x86.",
            "  • level0   : Inferencia en GPU Intel Arc (Level Zero).",
            "  • wasm     : Ejecución directa en navegador con JS Bridge.",
        ],
        "key_points": [
            "• Abstracción unificada: cambia de motor sin detener la simulación.",
            "• Cero dependencias: un único binario o un único archivo WASM.",
        ],
    },
    {
        "output": "tarjeta_b4_04_jarvis_qa.png",
        "badge": "BLOQUE 4 // DUDAS & PREGUNTAS CON JARVIS",
        "title": "Go en Producción de ML y el Salto a la Web con WASM",
        "source_file": "11-juego-final/pizarra.go",
        "line_start": 1,
        "line_end": 35,
        "focus_lines": (1, 35),
        "right_header": "PREGUNTAS DE JARVIS // COPILOTO IA",
        "terminal_lines": [
            "1. ¿Por qué desplegar inferencia en Go frente a Python?",
            "   -> Binario estático, memoria controlada y concurrencia.",
            "",
            "2. ¿Qué ventajas aporta compilar a WebAssembly (WASM)?",
            "   -> Divulgación accesible: 60 FPS sin instalar nada.",
            "",
            "• Serving con latencia de microsegundos en microservicios Go.",
            "• El alumno ve la matemática cobrando vida en el navegador.",
        ],
        "key_points": [
            "• Go brilla en la fase de Serving: ligero, robusto y concurrente.",
            "• WASM democratiza la visualización de Deep Learning.",
        ],
    },
    # --- BLOQUE 5 (RISC-V & RVV 1.0) ---
    {
        "output": "tarjeta_b5_01_riscv_rvv.png",
        "badge": "BLOQUE 5 // EDGE AI EN SILICIO LIBRE",
        "title": "12-riscv-rvv: Vectorización RVV 1.0 en CanMV-K230",
        "source_file": "12-riscv-rvv/vector_riscv64.s",
        "line_start": 1,
        "line_end": 34,
        "focus_lines": (9, 25),
        "right_header": "CROSS-COMPILE // GOOS=linux GOARCH=riscv64",
        "terminal_lines": [
            "$ CGO_ENABLED=0 GOOS=linux GOARCH=riscv64 \\",
            "    GORISCV64=rva22u64 go build -o neuron_k230 .",
            "$ file neuron_k230",
            "neuron_k230: ELF 64-bit LSB executable, UCB RISC-V",
            "",
            "Target SoC: Kendryte K230 (T-Head C908 + RVV 1.0)",
            "VPU: 128-bit Vector Length Agnostic (VSETVLI)",
        ],
        "key_points": [
            "• AVX usa registros fijos (256b); RVV adapta la longitud con VSETVLI.",
            "• Binario Go estático listo para desplegar en Linux K230.",
        ],
    },
]


def main():
    parser = argparse.ArgumentParser(description="Genera tarjetas de código 1920x1080 para vídeos de Go & ML.")
    parser.add_argument("--only", default=None, help="Filtra por subcadena en el nombre de salida")
    args = parser.parse_args()

    generated = 0
    for spec in CARD_SPECS:
        if args.only and args.only not in spec["output"]:
            continue
        if render_card(spec):
            generated += 1

    print(f"[✓] Proceso finalizado. Tarjetas generadas: {generated}")


if __name__ == "__main__":
    main()
