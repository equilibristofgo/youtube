#!/usr/bin/env bash
set -e

# capturar_ebiten.sh
# Graba clips limpios en X11 de los simuladores Ebiten (10-neuron-js-golang / 11-juego-final)
# hacia youtube/clips/ para su montaje como B-Roll en Blender VSE.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SANDBOX_NYU="${SANDBOX_NYU_DIR:-/home/jose/workspace/equilibristofgo/sandbox/14_nyu_00}"
CLIPS_DIR="${PROJECT_DIR}/clips"
mkdir -p "$CLIPS_DIR"

TARGET="${1:-manifold}"
DURATION="${2:-25}"
FPS="${3:-60}"
DISPLAY_ID="${DISPLAY:-:0.0}"

usage() {
    echo "Uso: $0 [xor|manifold] [duracion_seg] [fps]"
    echo "  xor       Graba 10-neuron-js-golang -> clips/ebiten_xor.mp4"
    echo "  manifold  Graba 11-juego-final      -> clips/ebiten_manifold.mp4"
    exit 1
}

case "$TARGET" in
    xor)
        APP_DIR="${SANDBOX_NYU}/10-neuron-js-golang"
        OUT_FILE="${CLIPS_DIR}/ebiten_xor.mp4"
        WIN_HINT="Neuron"
        ;;
    manifold)
        APP_DIR="${SANDBOX_NYU}/11-juego-final"
        OUT_FILE="${CLIPS_DIR}/ebiten_manifold.mp4"
        WIN_HINT="Deep Space"
        ;;
    *)
        usage
        ;;
esac

if [ ! -d "$APP_DIR" ]; then
    echo "[!] No se encuentra el directorio del simulador: $APP_DIR"
    exit 1
fi

echo "[*] Lanzando simulador en $APP_DIR..."
(cd "$APP_DIR" && go run .) &
APP_PID=$!

cleanup() {
    if kill -0 "$APP_PID" 2>/dev/null; then
        kill "$APP_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

sleep 3

GRAB_ARGS=(-video_size "1920x1080" -i "${DISPLAY_ID}+0,0")

if command -v xdotool >/dev/null 2>&1; then
    WIN_ID=$(xdotool search --name "$WIN_HINT" 2>/dev/null | head -n 1 || true)
    if [ -n "$WIN_ID" ]; then
        eval "$(xdotool getwindowgeometry --shell "$WIN_ID")"
        if [ -n "$WIDTH" ] && [ -n "$HEIGHT" ]; then
            # Asegurar dimensiones pares para libx264
            W=$((WIDTH - (WIDTH % 2)))
            H=$((HEIGHT - (HEIGHT % 2)))
            GRAB_ARGS=(-video_size "${W}x${H}" -i "${DISPLAY_ID}+${X},${Y}")
        fi
        xdotool windowactivate "$WIN_ID" || true
    fi
else
    echo "[i] Nota: 'xdotool' no está instalado; grabando captura de pantalla X11 (${DISPLAY_ID}) durante ${DURATION}s."
    echo "    (Instala 'xdotool' si deseas automatizar pulsaciones de teclas y recorte exacto de ventana)."
fi

echo "[*] Grabando ${DURATION}s @ ${FPS}fps en ${OUT_FILE}..."
ffmpeg -y -loglevel warning \
    -f x11grab -framerate "$FPS" "${GRAB_ARGS[@]}" \
    -t "$DURATION" \
    -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
    "$OUT_FILE" &
FF_PID=$!

if command -v xdotool >/dev/null 2>&1 && [ -n "${WIN_ID:-}" ]; then
    if [ "$TARGET" = "manifold" ]; then
        sleep 2 && xdotool key --window "$WIN_ID" t || true
        sleep 5 && xdotool key --window "$WIN_ID" s || true
        sleep 5 && xdotool key --window "$WIN_ID" 2 || true
        sleep 5 && xdotool key --window "$WIN_ID" 3 || true
    else
        sleep 2
        for _ in $(seq 1 15); do
            xdotool key --window "$WIN_ID" Up || true
            sleep 0.4
        done
    fi
fi

wait "$FF_PID"
echo "[✓] Clip Ebiten guardado en: ${OUT_FILE}"

