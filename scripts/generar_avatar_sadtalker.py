#!/usr/bin/env python3
"""
generar_avatar_sadtalker.py

Genera avatares animados de Jose usando SadTalker en la GPU Intel Arc (XPU).
Reutiliza la instalación y pesos en /home/jose/workspace/sandbox/SadTalker
(enlazados a /mnt/registry-data/general-backup/).

Soporta tanto un clip individual (--audio / --output) como generación por lotes
leyendo `audio/manifest_audio.json` (--from-manifest).
"""

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SADTALKER_DIR = os.environ.get("SADTALKER_DIR", "/home/jose/workspace/sandbox/SadTalker")
VENV_PYTHON = os.path.join(SADTALKER_DIR, ".venv", "bin", "python")

DEFAULT_IMAGE = os.path.join(PROJECT_DIR, "presentador_podcast_avatar.jpg")
DEFAULT_AUDIO = os.path.join(PROJECT_DIR, "audio", "audio_locucion.wav")
DEFAULT_MANIFEST = os.path.join(PROJECT_DIR, "audio", "manifest_audio.json")
CLIPS_DIR = os.path.join(PROJECT_DIR, "clips")


def run_sadtalker_one(
    image_path: str,
    audio_path: str,
    target_output: str,
    mode: str = "crop512",
    size: int = 512,
    pose_style: int = 0,
    expression_scale: float = 1.0,
    enhancer: str = None,
    device: str = "xpu",
):
    if not os.path.exists(SADTALKER_DIR) or not os.path.exists(VENV_PYTHON):
        print(f"[!] Error: SadTalker o su .venv no existen en {SADTALKER_DIR}")
        sys.exit(1)

    if not os.path.exists(image_path):
        print(f"[!] Error: No se encuentra la imagen {image_path}")
        sys.exit(1)

    if not os.path.exists(audio_path):
        print(f"[!] Error: No se encuentra el audio {audio_path}")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(target_output)), exist_ok=True)
    tmp_base = os.path.join(SADTALKER_DIR, "results_tmp")
    os.makedirs(tmp_base, exist_ok=True)

    with tempfile.TemporaryDirectory(dir=tmp_base) as temp_results_dir:
        cmd = [
            VENV_PYTHON,
            "inference.py",
            "--device", device,
            "--driven_audio", os.path.abspath(audio_path),
            "--source_image", os.path.abspath(image_path),
            "--result_dir", temp_results_dir,
            "--size", str(size),
            "--batch_size", "1",
            "--pose_style", str(pose_style),
            "--expression_scale", str(expression_scale),
        ]

        if mode == "crop512":
            cmd += ["--preprocess", "crop"]
            if enhancer and enhancer != "none":
                cmd += ["--enhancer", enhancer]
        elif mode == "still":
            cmd += ["--preprocess", "crop", "--still"]
            if enhancer and enhancer != "none":
                cmd += ["--enhancer", enhancer]
        elif mode == "full":
            enh = enhancer or "gfpgan"
            if enh != "none":
                cmd += ["--preprocess", "full", "--enhancer", enh]
            else:
                cmd += ["--preprocess", "full"]
        elif mode == "full_still":
            enh = enhancer or "gfpgan"
            if enh != "none":
                cmd += ["--preprocess", "full", "--still", "--enhancer", enh]
            else:
                cmd += ["--preprocess", "full", "--still"]

        env = os.environ.copy()
        if device == "xpu":
            env["ONEAPI_DEVICE_SELECTOR"] = "level_zero:gpu"

        print(f"[*] Lanzando SadTalker (Modo: {mode}, Device: {device}) -> {os.path.basename(target_output)}")
        result = subprocess.run(cmd, cwd=SADTALKER_DIR, env=env)
        if result.returncode != 0:
            print(f"[!] Error ejecutando SadTalker (código {result.returncode})")
            sys.exit(result.returncode)

        mp4_files = glob.glob(os.path.join(temp_results_dir, "**", "*.mp4"), recursive=True)
        if not mp4_files:
            print(f"[!] Error: No se encontró ningún vídeo generado en {temp_results_dir}")
            sys.exit(1)

        latest_video = max(mp4_files, key=os.path.getmtime)
        shutil.copyfile(latest_video, target_output)
        print(f"[✓] Avatar guardado en: {target_output}")


def main():
    parser = argparse.ArgumentParser(description="Genera el avatar animado de Jose con SadTalker.")
    parser.add_argument("--image", default=DEFAULT_IMAGE, help="Ruta a la imagen del avatar")
    parser.add_argument("--audio", default=DEFAULT_AUDIO, help="Ruta al audio individual")
    parser.add_argument("--mode", default="crop512", choices=["crop512", "full", "still", "full_still"],
                        help="Modo: crop512/still (para PiP) o full/full_still (plató 16:9)")
    parser.add_argument("--output", default=None, help="Ruta del archivo de vídeo MP4 resultante")
    parser.add_argument("--size", type=int, default=512, choices=[256, 512])
    parser.add_argument("--pose_style", type=int, default=0)
    parser.add_argument("--expression_scale", type=float, default=1.0)
    parser.add_argument("--enhancer", default=None, choices=["gfpgan", "RestoreFormer", "none"])
    parser.add_argument("--device", default="xpu", choices=["xpu", "cuda", "cpu"])
    parser.add_argument("--from-manifest", action="store_true", help="Procesa todas las escenas de Jose del manifest")
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
            if scene.get("speaker") != "jose":
                continue
            scene_id = scene["id"]
            audio_abs = os.path.join(PROJECT_DIR, scene["audio"])
            mode = scene.get("avatar_mode", "full" if scene.get("layout") in ("intro", "outro") else "crop512")
            out_path = os.path.join(CLIPS_DIR, f"jose_{scene_id}.mp4")
            if not args.force and os.path.exists(out_path):
                print(f"[=] Saltando clip existente: {out_path}")
                continue
            run_sadtalker_one(
                image_path=args.image,
                audio_path=audio_abs,
                target_output=out_path,
                mode=mode,
                size=args.size,
                pose_style=args.pose_style,
                expression_scale=args.expression_scale,
                enhancer=args.enhancer,
                device=args.device,
            )
    else:
        target = args.output or os.path.join(CLIPS_DIR, f"jose_avatar_{args.mode}.mp4")
        run_sadtalker_one(
            image_path=args.image,
            audio_path=args.audio,
            target_output=target,
            mode=args.mode,
            size=args.size,
            pose_style=args.pose_style,
            expression_scale=args.expression_scale,
            enhancer=args.enhancer,
            device=args.device,
        )


if __name__ == "__main__":
    main()

