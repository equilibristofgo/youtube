#!/usr/bin/env python3
"""
generar_avatar_echomimic.py

Automatiza la generación del avatar animado con sincronización labial
usando EchoMimic en GPU Intel Arc (XPU / FP16), reutilizando la instalación
de /home/jose/workspace/sandbox/EchoMimic.
"""

import argparse
import os
import subprocess
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ECHOMIMIC_DIR = os.environ.get("ECHOMIMIC_DIR", "/home/jose/workspace/sandbox/EchoMimic")
VENV_PYTHON = os.path.join(ECHOMIMIC_DIR, ".venv", "bin", "python")

DEFAULT_IMAGE = os.path.join(PROJECT_DIR, "presentador_podcast_avatar.jpg")
DEFAULT_AUDIO = os.path.join(PROJECT_DIR, "audio", "audio_locucion.wav")
DEFAULT_OUTPUT = os.path.join(PROJECT_DIR, "clips", "jose_echomimic.mp4")


def main():
    parser = argparse.ArgumentParser(description="Genera el avatar animado con EchoMimic en GPU Intel Arc.")
    parser.add_argument("--image", default=DEFAULT_IMAGE, help="Ruta a la imagen del avatar")
    parser.add_argument("--audio", default=DEFAULT_AUDIO, help="Ruta al archivo de audio de locución")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Ruta del vídeo final resultante")
    parser.add_argument("--device", default="xpu", choices=["xpu", "cuda", "cpu", "auto"])
    parser.add_argument("--max_frames", type=int, default=6000)
    parser.add_argument("--steps", type=int, default=6)
    parser.add_argument("--context_overlap", type=int, default=3)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    args = parser.parse_args()

    if not os.path.exists(ECHOMIMIC_DIR) or not os.path.exists(VENV_PYTHON):
        print(f"[!] Error: EchoMimic o su .venv no se encuentran en {ECHOMIMIC_DIR}")
        sys.exit(1)

    if not os.path.exists(args.image):
        print(f"[!] Error: No se encuentra la imagen {args.image}")
        sys.exit(1)

    if not os.path.exists(args.audio):
        print(f"[!] Error: No se encuentra el audio {args.audio}")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    img_abs = os.path.abspath(args.image)
    audio_abs = os.path.abspath(args.audio)
    yaml_content = f"""pretrained_base_model_path: "./pretrained_weights/sd-image-variations-diffusers/"
pretrained_vae_path: "./pretrained_weights/sd-vae-ft-mse/"
audio_model_path: "./pretrained_weights/audio_processor/whisper_tiny.pt"
denoising_unet_path: "./pretrained_weights/denoising_unet_acc.pth"
reference_unet_path: "./pretrained_weights/reference_unet.pth"
face_locator_path: "./pretrained_weights/face_locator.pth"
motion_module_path: "./pretrained_weights/motion_module_acc.pth"
inference_config: "./configs/inference/inference_v2.yaml"
weight_dtype: "fp16"
test_cases:
  "{img_abs}":
    - "{audio_abs}"
"""

    config_path = os.path.join(ECHOMIMIC_DIR, "configs", "prompts", "run_equilibristofgo.yaml")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    env = os.environ.copy()
    if args.device == "xpu":
        env["ONEAPI_DEVICE_SELECTOR"] = "level_zero:gpu"

    cmd = [
        VENV_PYTHON,
        "infer_audio2vid_acc.py",
        "--config", config_path,
        "-W", str(args.width),
        "-H", str(args.height),
        "-L", str(args.max_frames),
        "--steps", str(args.steps),
        "--context_overlap", str(args.context_overlap),
        "--device", args.device,
        "--output_file", os.path.abspath(args.output),
    ]

    print(f"[*] Lanzando EchoMimic en {args.device}: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ECHOMIMIC_DIR, env=env)
    if result.returncode != 0:
        print(f"[!] Error al ejecutar EchoMimic (código {result.returncode})")
        sys.exit(result.returncode)

    print(f"[✓] Vídeo EchoMimic generado: {args.output}")


if __name__ == "__main__":
    main()

