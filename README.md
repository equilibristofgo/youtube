# Pipeline de Vídeo Automatizado: Equilibristas de Golang

Generación programática de vídeos técnicos de Inteligencia Artificial y Go para el canal de YouTube **@equilibristofgolang6247**, combinando:
* **Locución en Dúo:** Host (Jose) y Copiloto IA (Orbe holográfico de Jarvis).
* **Animación Facial por IA:** SadTalker / EchoMimic acelerado en **GPU Intel Arc (XPU / Level Zero)**.
* **Tarjetas de Código Híbridas 1080p:** Sintaxis en Go con resaltado de líneas, terminal y gráficas reales de `gonum/plot`.
* **Simulación Interactiva:** Captura automatizada a 60 FPS de simuladores Ebiten (`10-neuron-js-golang` y `11-juego-final`).
* **Montaje Headless en Blender VSE:** Composición por capas y renderizado 1080p a 25 FPS sin abrir GUI.
* **Publicación Directa:** Subida automatizada con metadatos y timestamps usando `yutu` (OAuth 2.0).

---

## 🛠️ Requisitos de Sistema (Intel Arc GPU)

1. **Hardware & Driver:**
   * GPU Intel Arc (p. ej. Arc B580 / A770) con kernel driver `xe` y soporte Level Zero (`intel-level-zero-gpu`).
   * Al menos 16 GB de RAM.
2. **Software del Host:**
   * **Go 1.24+**
   * **Blender 4.2+ o 4.3+** en el `PATH` (`blender -v`).
   * **FFmpeg 6+ o 7+** con soporte `x11grab` y `libx264`.
   * **Python 3.10+** con librerías: `Pillow`, `numpy`, `requests`, `python-xlib`.
   * CLI de subida **yutu** instalado en `/home/jose/go/bin/yutu` o en `$PATH`.
3. **Servicios Docker:**
   * Contenedor `kokoro-tts` en puerto local `8880` (`kokoro-tts:v2`, CPU).
   * (Opcional) Contenedor `f5-tts` en puerto `8880` para clonación de voz en XPU.
4. **Modelos de Animación (SadTalker / EchoMimic):**
   * Repositorio SadTalker clonado con entorno virtual (`.venv`) y pesos descargados (se busca por defecto en `/home/jose/workspace/sandbox/SadTalker` o mediante la variable de entorno `SADTALKER_DIR`).

---

## 📁 Estructura del Proyecto

```text
youtube/
├── start-services.sh               # Orquestador CLI principal
├── AGENTS.md                       # Especificación técnica completa para agentes IA
├── presentador_podcast_avatar.jpg  # Imagen base del presentador en plató 16:9
├── audio/
│   ├── guion_escenas.json          # Guion activo en ejecución
│   ├── guion_video3_completo.json  # Guion definitivo de la Sesión 3
│   ├── guion_video4_completo.json  # Guion definitivo de la Sesión 4
│   └── manifest_audio.json         # Partitura temporal exacta con duraciones por escena
├── tarjetas/                       # Tarjetas de código generadas en 1920x1080
├── clips/                          # Clips intermedios de avatares, Orbe Jarvis y Ebiten
├── docs/                           # Escaleta maestra de la tanda 2+1 de 15 min
├── scripts/                        # Motores de síntesis, animación, captura y montaje
└── output/                         # Vídeos finales .mp4 renderizados
```

---

## 🚀 Flujo de Trabajo Rápido

```bash
# 1. Generar todas las tarjetas de código 1080p
./start-services.sh cards

# 2. Grabar los clips interactivos de Ebiten a 60 FPS
python3 scripts/auto_record_ebiten.py manifold 35
python3 scripts/auto_record_ebiten.py xor 25

# 3. Sintetizar las voces del guion actual (Jose + Jarvis)
./start-services.sh audio

# 4. Generar el clip reactivo del Orbe de Jarvis
./start-services.sh jarvis

# 5. Generar las animaciones faciales de Jose en GPU Intel Arc
./start-services.sh avatar

# 6. Montar y renderizar el máster en Blender VSE
./start-services.sh render output/mi_video_master.mp4

# 7. Subir a YouTube (unlisted / public)
./start-services.sh upload unlisted output/mi_video_master.mp4 "Título del Vídeo"
```

---

## 🔐 Autenticación de YouTube

Las credenciales **NO** se almacenan en git. Cada desarrollador debe:
1. Colocar su `client_secret.json` descargado de Google Cloud Console (OAuth Desktop App).
2. Ejecutar por primera vez en esta carpeta:
   ```bash
   yutu auth
   ```
3. Seleccionar la cuenta de marca **Equilibrist Of GoLang** en el navegador para generar `youtube.token.json`.

