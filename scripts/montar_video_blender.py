#!/usr/bin/env python3
"""
montar_video_blender.py

Script headless para Blender 4.x Video Sequence Editor (VSE).
Lee `audio/manifest_audio.json` y ensambla el vídeo tecnológico:
  - Escenas 'intro' / 'outro': Avatar de Jose a pantalla completa (1920x1080) + rótulo.
  - Escenas 'code' / 'graph' / 'sim': Tarjeta de código o clip Ebiten en Canal 1 +
    avatar de Jose en Picture-in-Picture (PiP) en la esquina inferior derecha.
  - Escenas 'jarvis': Tarjeta de código/pregunta en Canal 1 + Orbe holográfico de
    Jarvis en el recuadro PiP (o a pantalla completa si visual está vacío).
"""

import argparse
import json
import os
import sys
import bpy

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_MANIFEST = os.path.join(PROJECT_DIR, "audio", "manifest_audio.json")
DEFAULT_OUTPUT = os.path.join(PROJECT_DIR, "output", "video_final_go_ml.mp4")
IMG_BG = os.path.join(PROJECT_DIR, "presentador_podcast_avatar.jpg")

# Coordenadas exactas del marco "LIVE CAM // HOST & JARVIS" en tarjetas_codigo.py
# Viewport interior: x=1500..1850 (centro=1675, ancho=350), y=685..1035 (centro=860, alto=350)
PIP_SIZE = 350.0
PIP_OFFSET_X = 1675.0 - 960.0   # +715.0 px desde el centro del lienzo
PIP_OFFSET_Y = 540.0 - 860.0    # -320.0 px (eje Y de Blender es positivo hacia arriba)


def parse_blender_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser(description="Montaje VSE de Equilibristas de Golang.")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Ruta a manifest_audio.json")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Ruta del MP4 final")
    parser.add_argument("--fps", type=int, default=25, help="FPS de la secuencia (por defecto 25)")
    parser.add_argument("--render", action="store_true", help="Ejecuta el renderizado MP4")
    return parser.parse_args(argv)


def fit_strip_fullscreen(strip, canvas_w=1920.0, canvas_h=1080.0):
    orig_w, orig_h = 0, 0
    if hasattr(strip, "elements") and len(strip.elements) > 0:
        orig_w = strip.elements[0].orig_width
        orig_h = strip.elements[0].orig_height
    if orig_w > 0 and orig_h > 0:
        scale = max(canvas_w / orig_w, canvas_h / orig_h)
        strip.transform.scale_x = scale
        strip.transform.scale_y = scale


def fit_strip_pip(strip):
    orig_w, orig_h = 512, 512
    if hasattr(strip, "elements") and len(strip.elements) > 0:
        if strip.elements[0].orig_width > 0 and strip.elements[0].orig_height > 0:
            orig_w = strip.elements[0].orig_width
            orig_h = strip.elements[0].orig_height
    scale = PIP_SIZE / max(orig_w, orig_h)
    strip.transform.scale_x = scale
    strip.transform.scale_y = scale
    strip.transform.offset_x = PIP_OFFSET_X
    strip.transform.offset_y = PIP_OFFSET_Y
    strip.blend_type = 'ALPHA_OVER'


def add_lower_third(seq, channel, start_frame, end_frame, text, name):
    strip_text = seq.new_effect(
        name=name,
        type='TEXT',
        channel=channel,
        frame_start=start_frame,
        frame_end=min(end_frame, start_frame + 125),
    )
    strip_text.text = text
    strip_text.font_size = 36
    strip_text.location[0] = 0.5
    strip_text.location[1] = 0.09
    strip_text.color = (0.94, 0.96, 0.99, 1.0)
    strip_text.use_box = True
    strip_text.box_color = (0.05, 0.07, 0.10, 0.80)
    strip_text.box_margin = 0.03


def setup_vse(manifest_path: str, output_path: str, fps: int = 25, do_render: bool = False):
    if not os.path.exists(manifest_path):
        print(f"[!] Error: No existe el manifest {manifest_path}")
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    scenes = manifest.get("scenes", [])
    if not scenes:
        print("[!] Error: El manifest no contiene escenas.")
        sys.exit(1)

    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'

    if not scene.sequence_editor:
        scene.sequence_editor_create()
    seq = scene.sequence_editor.sequences
    for s in list(seq):
        seq.remove(s)

    current_frame = 1

    for idx, sc in enumerate(scenes):
        sc_id = sc["id"]
        speaker = sc.get("speaker", "jose")
        layout = sc.get("layout", "code")
        audio_abs = os.path.join(PROJECT_DIR, sc["audio"])
        visual_rel = sc.get("visual", "")
        visual_abs = os.path.join(PROJECT_DIR, visual_rel) if visual_rel else ""

        if not os.path.exists(audio_abs):
            print(f"[!] Error: Falta audio para escena {sc_id}: {audio_abs}")
            sys.exit(1)

        strip_snd = seq.new_sound(
            name=f"Snd_{sc_id}",
            filepath=audio_abs,
            channel=2,
            frame_start=current_frame,
        )
        scene_frames = max(1, strip_snd.frame_final_duration)
        end_frame = current_frame + scene_frames

        prefix = "jose" if speaker == "jose" else "jarvis"
        avatar_clip = os.path.join(PROJECT_DIR, "clips", f"{prefix}_{sc_id}.mp4")

        if layout in ("intro", "outro") or not visual_abs or not os.path.exists(visual_abs):
            # Pantalla completa: avatar + fondo de estudio si el avatar es 512x512
            if os.path.exists(avatar_clip):
                strip_av = seq.new_movie(
                    name=f"Full_{sc_id}",
                    filepath=avatar_clip,
                    channel=3,
                    frame_start=current_frame,
                )
                orig_w = strip_av.elements[0].orig_width if strip_av.elements else 512
                orig_h = strip_av.elements[0].orig_height if strip_av.elements else 512
                if orig_w < 1920 and os.path.exists(IMG_BG):
                    strip_bg = seq.new_image(
                        name=f"Bg_{sc_id}",
                        filepath=IMG_BG,
                        channel=1,
                        frame_start=current_frame,
                    )
                    strip_bg.frame_final_duration = scene_frames
                    fit_strip_fullscreen(strip_bg)
                    scale = 1080.0 / max(1, orig_h)
                    strip_av.transform.scale_x = scale
                    strip_av.transform.scale_y = scale
                    strip_av.blend_type = 'ALPHA_OVER'
                else:
                    fit_strip_fullscreen(strip_av)
                strip_av.frame_final_end = end_frame
            elif os.path.exists(IMG_BG):
                strip_bg = seq.new_image(
                    name=f"Bg_{sc_id}",
                    filepath=IMG_BG,
                    channel=1,
                    frame_start=current_frame,
                )
                strip_bg.frame_final_duration = scene_frames
                fit_strip_fullscreen(strip_bg)

            if sc.get("title"):
                add_lower_third(seq, 5, current_frame, end_frame, sc["title"], f"Title_{sc_id}")

        else:
            # Layout híbrido PiP: tarjeta/vídeo en Canal 1 + avatar/orbe en Canal 4
            ext = os.path.splitext(visual_abs)[1].lower()
            if ext in (".mp4", ".mov", ".mkv", ".webm"):
                strip_vis = seq.new_movie(
                    name=f"Vis_{sc_id}",
                    filepath=visual_abs,
                    channel=1,
                    frame_start=current_frame,
                )
                fit_strip_fullscreen(strip_vis)
                strip_vis.frame_final_end = end_frame
            else:
                strip_vis = seq.new_image(
                    name=f"Vis_{sc_id}",
                    filepath=visual_abs,
                    channel=1,
                    frame_start=current_frame,
                )
                strip_vis.frame_final_duration = scene_frames
                fit_strip_fullscreen(strip_vis)

            if os.path.exists(avatar_clip):
                strip_pip = seq.new_movie(
                    name=f"PiP_{sc_id}",
                    filepath=avatar_clip,
                    channel=4,
                    frame_start=current_frame,
                )
                fit_strip_pip(strip_pip)
                strip_pip.frame_final_end = end_frame
            else:
                print(f"[!] Aviso: No existe clip PiP {avatar_clip}, escena {sc_id} solo con visual.")

        print(f"[+] Escena {idx+1}/{len(scenes)} '{sc_id}' ({speaker}/{layout}): frames {current_frame}..{end_frame - 1} ({scene_frames / fps:.2f}s)")
        current_frame = end_frame

    scene.frame_start = 1
    scene.frame_end = max(1, current_frame - 1)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    scene.render.filepath = os.path.abspath(output_path)
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.ffmpeg.audio_codec = 'AAC'
    scene.render.ffmpeg.audio_bitrate = 192

    total_sec = scene.frame_end / float(fps)
    print(f"[✓] Línea de tiempo lista: {scene.frame_end} frames ({total_sec:.2f}s) -> {output_path}")

    if do_render:
        print(f"[*] Renderizando vídeo final en Blender VSE...")
        bpy.ops.render.render(animation=True)
        print(f"[✓] Render completado: {output_path}")


if __name__ == "__main__":
    args = parse_blender_args()
    setup_vse(args.manifest, args.output, fps=args.fps, do_render=args.render)

