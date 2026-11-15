# AGENTS.md — Pipeline de Producción de Vídeo: Equilibristas de Golang

Este directorio adapta la cadena de producción de vídeo automatizada para el canal **Equilibristas de Golang**, combinando código real en Go, gráficas de `gonum/plot`, simuladores `Ebiten` y locución en dúo (**Jose** + **Orbe Jarvis**).

---

## 1. Arquitectura de Activos y Reutilización en Disco

Para evitar duplicar decenas de gigabytes de pesos de IA en el NVMe, este pipeline reutiliza directamente las instalaciones y cachés compartidas:
* **SadTalker (Jose Avatar 2.7K / PiP):** `/home/jose/workspace/sandbox/SadTalker` (enlazado a `/mnt/registry-data/general-backup/`).
* **EchoMimic (alternativa):** `/home/jose/workspace/sandbox/EchoMimic`.
* **Contenedores TTS (Puerto 8880 compartido):**
  * `f5-tts` (`f5-tts:latest`, GPU Intel Arc XPU): voz clonada **`jose`**.
  * `kokoro-tts` (`kokoro-tts:v2`, CPU): voz **`em_alex`** para **Jarvis**.
  * *Regla crítica:* Nunca arrancar ambos contenedores a la vez; `scripts/generar_audio_duo.py` agrupa las escenas por locutor y conmuta los contenedores secuencialmente.

---

## 2. Mapa de Archivos

| Ruta | Función |
| :--- | :--- |
| `start-services.sh` | Orquestador CLI (`cards`, `audio`, `avatar`, `jarvis`, `ebiten`, `render`, `prototipo`, `upload`). |
| `presentador_podcast_avatar.jpg` | Imagen base 16:9 de Jose en el plató de podcast. |
| `client_secret.json` | Credenciales OAuth 2.0 para YouTube Data API (pendiente autenticar `youtube.token.json` del canal técnico). |
| `audio/` | Guiones por escena (`guion_prototipo_b3.json`, `guion_escenas.json`), `.wav` generados y `manifest_audio.json`. |
| `tarjetas/` | Tarjetas de código 1920x1080 generadas con `generar_tarjetas_codigo.py` (con hueco PiP reservado). |
| `clips/` | Vídeos generados por escena (`jose_*.mp4`, `jarvis_*.mp4`) y grabaciones Ebiten (`ebiten_*.mp4`). |
| `docs/` | Escaletas detalladas de la tanda de 2+1 vídeos de 15 minutos (`escaleta_2_mas_1_videos_15min.md`). |
| `output/` | Vídeos finales exportados desde Blender VSE (`prototipo_bloque3_talkback.mp4`, etc.). |

---

## 3. Pipeline Paso a Paso

```bash
# 1. Generar las tarjetas de código desde sandbox/14_nyu_00
./start-services.sh cards

# 2. Sintetizar voces en dúo (Jose F5-TTS + Jarvis Kokoro-TTS)
./start-services.sh audio [--prototipo]

# 3. Generar clips de avatar de Jose en GPU Intel Arc (SadTalker)
./start-services.sh avatar

# 4. Generar clips del Orbe reactivo de Jarvis en CPU (Pillow + FFmpeg)
./start-services.sh jarvis

# 5. (Opcional) Grabar clips reales de Ebiten a 60 FPS en X11
./start-services.sh ebiten manifold 25 60

# 6. Montar y renderizar el máster 1080p @ 25fps en Blender VSE
./start-services.sh render output/prototipo_bloque3_talkback.mp4

# Todo el prototipo de una sola vez:
./start-services.sh prototipo
```

---

## 4. Layout Visual y Coordenadas PiP

Todas las tarjetas generadas por `scripts/generar_tarjetas_codigo.py` reservan en la esquina inferior derecha la caja **`LIVE CAM // HOST & JARVIS`** (`x=1492..1860, y=650..1040`, viewport interior de `350x350` centrado en `(1675, 860)`).
`scripts/montar_video_blender.py` posiciona los clips cuadrados `512x512` (`crop512`/`still` para Jose y `pip` para el Orbe de Jarvis) en esas coordenadas exactas (`offset_x=+715, offset_y=-320`) sobre el Canal 4, manteniendo intactas la columna de código y la gráfica/terminal.

