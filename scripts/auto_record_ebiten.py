#!/usr/bin/env python3
"""
auto_record_ebiten.py

Lanza los juegos Ebiten de NYU (10-neuron-js-golang y 11-juego-final),
detecta sus ventanas X11 mediante python-xlib, envía pulsaciones automáticas
y graba clips B-Roll a 60 FPS con FFmpeg de forma 100% autónoma.
"""

import os
import subprocess
import sys
import time
from Xlib import X, display, XK
from Xlib.ext import xtest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SANDBOX_DIR = "/home/jose/workspace/equilibristofgo/sandbox/14_nyu_00"
CLIPS_DIR = os.path.join(PROJECT_DIR, "clips")
os.makedirs(CLIPS_DIR, exist_ok=True)


def get_window_by_name(d, root, name_substring):
    """Busca recursivamente una ventana en X11 por subtítulo."""
    try:
        children = root.query_tree().children
    except Exception:
        return None

    for w in children:
        try:
            wm_name = w.get_wm_name()
            if wm_name and name_substring.lower() in wm_name.lower():
                return w
            res = get_window_by_name(d, w, name_substring)
            if res:
                return res
        except Exception:
            continue
    return None


def send_key(d, key_str):
    """Envía un keypress y keyrelease simulado con XTest."""
    keysym = XK.string_to_keysym(key_str)
    keycode = d.keysym_to_keycode(keysym)
    if keycode:
        xtest.fake_input(d, X.KeyPress, keycode)
        d.sync()
        time.sleep(0.05)
        xtest.fake_input(d, X.KeyRelease, keycode)
        d.sync()
        time.sleep(0.05)


def record_game(target="manifold", duration=25, fps=60):
    display_env = os.environ.get("DISPLAY", ":0.0")
    d = display.Display(display_env)
    root = d.screen().root

    if target == "manifold":
        app_dir = os.path.join(SANDBOX_DIR, "11-juego-final")
        out_file = os.path.join(CLIPS_DIR, "ebiten_manifold.mp4")
        win_hint = "Neural Levels"
    else:
        app_dir = os.path.join(SANDBOX_DIR, "10-neuron-js-golang")
        out_file = os.path.join(CLIPS_DIR, "ebiten_xor.mp4")
        win_hint = "Simulador XOR"

    print(f"[*] Lanzando simulador en {app_dir}...")
    proc = subprocess.Popen(["go", "run", "."], cwd=app_dir)

    try:
        # Esperar a que la ventana aparezca
        win = None
        for _ in range(30):
            time.sleep(0.5)
            win = get_window_by_name(d, root, win_hint)
            if win:
                break

        if not win:
            print(f"[!] No se encontró la ventana con título '{win_hint}'")
            return False

        geom = win.get_geometry()
        # Obtener coordenadas absolutas en pantalla
        tcoords = win.translate_coords(root, 0, 0)
        x = max(0, tcoords.x)
        y = max(0, tcoords.y)
        w = geom.width - (geom.width % 2)
        h = geom.height - (geom.height % 2)

        print(f"[✓] Ventana detectada: {w}x{h} en +{x}+{y}")

        # Enfocar la ventana
        win.set_input_focus(X.RevertToParent, X.CurrentTime)
        d.sync()

        # Iniciar grabación FFmpeg
        print(f"[*] Grabando {duration}s @ {fps}fps -> {out_file}...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-loglevel", "warning",
            "-f", "x11grab", "-framerate", str(fps),
            "-video_size", f"{w}x{h}",
            "-i", f"{display_env}+{x},{y}",
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
            out_file
        ]
        ff_proc = subprocess.Popen(ffmpeg_cmd)

        # Enviar comandos interactivos al juego según el objetivo
        time.sleep(1.5)
        if target == "manifold":
            print("[*] Simulando interacción: Enter (intro) -> T (train) -> S (sim) -> X (engine)...")
            send_key(d, "Return")
            time.sleep(1.0)
            send_key(d, "t") # Toggle Training
            time.sleep(2.0)
            send_key(d, "s") # Toggle Simulation
            time.sleep(4.0)
            send_key(d, "x") # Switch backend (Parallel)
            time.sleep(4.0)
            send_key(d, "x") # Switch backend (AVX)
            time.sleep(4.0)
            send_key(d, "p") # Speed up
            send_key(d, "p")
            time.sleep(4.0)
            send_key(d, "v") # Toggle Tension / Vector flow
        else:
            print("[*] Simulando interacción: Ajustando pesos con flechas...")
            for _ in range(12):
                send_key(d, "Up")
                time.sleep(0.4)
            for _ in range(6):
                send_key(d, "Right")
                time.sleep(0.4)

        ff_proc.wait()
        print(f"[✓] Grabación finalizada: {out_file}")
        return True

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "manifold"
    dur = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    record_game(target=target, duration=dur)
