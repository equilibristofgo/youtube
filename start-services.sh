#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    echo "Uso: $0 [start|stop|status|cards|audio|avatar|jarvis|ebiten|render|upload|prototipo|full]"
    echo ""
    echo "Comandos:"
    echo "  start [jose|jarvis]  Arranca el contenedor TTS deseado en puerto 8880 (por defecto jarvis)"
    echo "  stop                 Detiene f5-tts y kokoro-tts"
    echo "  status               Muestra estado de f5-tts, kokoro-tts y endpoint 8880"
    echo "  cards                Genera las tarjetas de código 1920x1080 en tarjetas/"
    echo "  audio [--prototipo]  Sintetiza audio en dúo (f5-tts 'jose' + kokoro-tts 'jarvis')"
    echo "  avatar               Genera clips de avatar Jose con SadTalker en GPU Intel Arc"
    echo "  jarvis               Genera clips del Orbe de Jarvis sincronizados con su WAV"
    echo "  ebiten [xor|manifold] Graba clips X11 de los simuladores Ebiten"
    echo "  render [out.mp4]     Monta y renderiza el máster en Blender VSE"
    echo "  upload [privacy] [file] [title] Sube el vídeo a YouTube con yutu"
    echo "  prototipo            Ejecuta la cadena completa del prototipo Bloque 3 (60-90s)"
    echo "  full                 Ejecuta cards -> audio -> avatar -> jarvis -> render"
    exit 1
}

start_tts() {
    local who="${1:-jarvis}"
    if [ "$who" = "jose" ]; then
        docker stop kokoro-tts >/dev/null 2>&1 || true
        echo -e "${BLUE}=== Arrancando f5-tts (Voz clonada 'jose', Puerto 8880) ===${NC}"
        docker start f5-tts
    else
        docker stop f5-tts >/dev/null 2>&1 || true
        echo -e "${BLUE}=== Arrancando kokoro-tts (Voz Jarvis 'em_alex', Puerto 8880) ===${NC}"
        docker start kokoro-tts
    fi
    show_status
}

stop_tts() {
    echo -e "${YELLOW}Deteniendo contenedores TTS...${NC}"
    docker stop f5-tts kokoro-tts >/dev/null 2>&1 || true
    echo -e "${GREEN}✓ Servicios TTS detenidos.${NC}"
}

show_status() {
    echo -e "${BLUE}=== Estado de contenedores TTS ===${NC}"
    docker ps -a --filter "name=f5-tts" --filter "name=kokoro-tts" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo -ne "Puerto 8880: "
    if curl -s -f http://localhost:8880/v1/models >/dev/null 2>&1 || curl -s -f http://localhost:8880/docs >/dev/null 2>&1; then
        echo -e "${GREEN}ONLINE${NC}"
    else
        echo -e "${RED}OFFLINE${NC}"
    fi
}

gen_cards() {
    echo -e "${BLUE}=== Generando tarjetas de código 1920x1080 ===${NC}"
    python3 "${SCRIPT_DIR}/scripts/generar_tarjetas_codigo.py" "$@"
}

gen_audio() {
    echo -e "${BLUE}=== Generando locuciones Dúo (Jose + Jarvis) ===${NC}"
    python3 "${SCRIPT_DIR}/scripts/generar_audio_duo.py" "$@"
}

gen_avatar() {
    echo -e "${BLUE}=== Generando clips avatar Jose (SadTalker XPU) ===${NC}"
    python3 "${SCRIPT_DIR}/scripts/generar_avatar_sadtalker.py" --from-manifest "$@"
}

gen_jarvis() {
    echo -e "${BLUE}=== Generando clips Orbe Jarvis (Pillow CPU) ===${NC}"
    python3 "${SCRIPT_DIR}/scripts/generar_avatar_jarvis_orb.py" --from-manifest "$@"
}

capture_ebiten() {
    echo -e "${BLUE}=== Capturando simulador Ebiten ===${NC}"
    "${SCRIPT_DIR}/scripts/capturar_ebiten.sh" "$@"
}

render_video() {
    local out_file="${1:-${SCRIPT_DIR}/output/video_final_go_ml.mp4}"
    echo -e "${BLUE}=== Renderizando máster en Blender VSE ===${NC}"
    blender -b -P "${SCRIPT_DIR}/scripts/montar_video_blender.py" -- --output "$out_file" --render
}

upload_video() {
    local privacy="${1:-unlisted}"
    local video_file="${2:-${SCRIPT_DIR}/output/video_final_go_ml.mp4}"
    local title="${3:-Equilibristas de Golang: Go & Machine Learning}"

    if [ ! -f "$video_file" ]; then
        echo -e "${RED}[!] No existe el vídeo: ${video_file}${NC}"
        exit 1
    fi
    if [ ! -f "${SCRIPT_DIR}/youtube.token.json" ]; then
        echo -e "${YELLOW}[!] Aviso: No hay youtube.token.json en ${SCRIPT_DIR}.${NC}"
        echo "    Asegúrate de autenticar yutu con la cuenta de Equilibristas de Golang."
    fi

    (cd "$SCRIPT_DIR" && /home/jose/go/bin/yutu video insert \
        --file "$video_file" \
        --title "$title" \
        --description 'Serie Equilibristas de Golang: Redes Neuronales y Machine Learning en Go, desde Gonum y Ebiten hasta RISC-V RVV 1.0.' \
        --tags 'golang,machine learning,deep learning,ebiten,gonum,riscv,intel arc' \
        --categoryId 28 \
        --privacy "$privacy" \
        --language es \
        --forKids=false \
        --containsSyntheticMedia=true \
        --yes)
}

run_prototipo() {
    gen_cards
    gen_audio --prototipo
    gen_avatar
    gen_jarvis
    render_video "${SCRIPT_DIR}/output/prototipo_bloque3_talkback.mp4"
    echo -e "${GREEN}✓ Prototipo Bloque 3 completado.${NC}"
}

run_full() {
    gen_cards
    gen_audio
    gen_avatar
    gen_jarvis
    render_video
    echo -e "${GREEN}✓ Pipeline completo finalizado.${NC}"
}

ACTION="${1:-status}"
shift || true

case "$ACTION" in
    start) start_tts "$@" ;;
    stop) stop_tts ;;
    status) show_status ;;
    cards) gen_cards "$@" ;;
    audio) gen_audio "$@" ;;
    avatar) gen_avatar "$@" ;;
    jarvis) gen_jarvis "$@" ;;
    ebiten) capture_ebiten "$@" ;;
    render) render_video "$@" ;;
    upload) upload_video "$@" ;;
    prototipo) run_prototipo ;;
    full) run_full ;;
    *) usage ;;
esac

