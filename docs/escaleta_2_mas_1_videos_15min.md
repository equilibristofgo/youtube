# Escaleta Maestra: Tanda de 2+1 Vídeos de 15 Minutos (Equilibristas de Golang)

Continuación oficial tras las Sesiones 1 y 2 grabadas en LiveKit (`Ghk5mH8soaI` y `JyzpeTP6Jxw`), ahora producida de forma programática y determinista en máquina local con **tarjetas de código de alta legibilidad + gráficas reales + clips Ebiten + Dúo Jose (F5-TTS/SadTalker) & Jarvis (Kokoro/Orbe)**.

---

## Vídeo 3 (Bloque 3 del Blog): Anatomía Visual del Aprendizaje (~15 min)
* **Objetivo:** Entender cómo aprende una red neuronal en Go puro: del bucle de entrenamiento XOR a las gráficas 2D con `gonum/plot` y el papel geométrico del peso y del sesgo.
* **Estructura temporal:**
  1. **00:00 - 01:30 | Intro (Jose Fullscreen):** Resumen de dónde lo dejamos en la Sesión 2 (multiplicación matricial con Gonum y GPU Intel Arc) y qué vamos a construir hoy.
  2. **01:30 - 05:30 | `07-train`: El Bucle de Entrenamiento XOR (Código + Terminal + Jose PiP):**
     * Forward Pass (`inputs * wHidden` -> `sigmoid`).
     * Cálculo de pérdida y derivada de la sigmoide (`s * (1 - s)`).
     * Backpropagation y ajuste por *Learning Rate*.
     * Salida real en consola convergiendo a `[0, 1, 1, 0]`.
  3. **05:30 - 08:00 | `08-sigmoid` & `09-sigmoid-graph`: La Curva en 'S' (Código + `sigmoid.png` + Jose PiP):**
     * Por qué acotar entre `0` y `1` y cómo `gonum/plot` dibuja la rampa en 2D.
  4. **08:00 - 11:00 | `10-neuron` & `10-neuron-temperatura`: Peso vs Sesgo (Código + PNGs + Jose PiP):**
     * Comparativa `sigmoid_vs_neuron.png`: el peso ($W$) escala la pendiente; el sesgo ($b$) traslada la curva.
     * Caso real de temperaturas por hora del día (`temperature_prediction.png`): distinguir las 12:00 de las 18:00.
     * Breve apunte del ecosistema moderno en Go: `Hugot` y `Cybertron`.
  5. **11:00 - 14:30 | Dudas y Preguntas (Dúo Jose + Orbe Jarvis):**
     * **Jarvis:** ¿Por qué la función Sigmoide ha caído en desuso en redes profundas frente a ReLU o GELU? (*Vanishing Gradient*).
     * **Jarvis:** ¿Cómo explicarías el sesgo (*bias*) a un gopher novato sin fórmulas?
  6. **14:30 - 15:00 | Cierre (Jose Fullscreen):** Adelanto de la Sesión 4 (pasamos de PNGs estáticos a 60 FPS en Ebiten).

---

## Vídeo 4 (Bloque 4 del Blog): La Vida en Tiempo Real y el Tejido Neuronal (~15 min)
* **Objetivo:** Convertir la teoría de NYU (Yann LeCun & Alfredo Canziani) en visualización interactiva a 60 FPS con Ebiten, WebAssembly y multiplexación de motores.
* **Estructura temporal:**
  1. **00:00 - 01:30 | Intro (Jose Fullscreen):** El salto de gráficas PNG estáticas a simulación interactiva en tiempo real.
  2. **01:30 - 05:00 | `10-neuron-js-golang`: Tú eres el Optimizador (Clip Ebiten + Código + Jose PiP):**
     * Nodos con *alpha* proporcional a la activación; sinapsis verdes (+) y rojas (-).
     * Entrenando y desentrenando XOR en vivo con las flechas y ajustando el *Learning Rate*.
  3. **05:00 - 11:00 | `11-juego-final`: Deep Space Stretching (Clip Ebiten 60 FPS + Jose PiP):**
     * La **Hipótesis del Manifold**: doblar y estirar la cuadrícula 2D ("la manta") para desenredar espirales y anillos.
     * La **Pizarra de Cálculo** en vivo (inspección tensorial capa por capa).
     * **Multiplexación de motores (`nn/`):** `standard`, `parallel`, `avx`, `oneapi`, `level0` y compilación a navegador en **WASM**.
  4. **11:00 - 14:30 | Dudas y Preguntas (Dúo Jose + Orbe Jarvis):**
     * **Jarvis:** ¿Es Go viable para producción de ML frente a Python/C++?
     * **Jarvis:** ¿Qué aporta compilar el simulador a WebAssembly (WASM) para divulgación técnica?
  5. **14:30 - 15:00 | Cierre (Jose Fullscreen):** Teaser del episodio extra: sacar las redes de nuestro PC hacia el silicio abierto RISC-V.

---

## Vídeo 5 (+1 Extra, Bloque 5 del Blog): Del Cloud al Silicio Libre: Go + ML sobre RISC-V (~15 min)
* **Objetivo:** Llevar nuestras neuronas en Go al Edge AI en una placa **CanMV-K230** (SoC Kendryte K230 Dual-Core RISC-V T-Head C908 con VPU **RVV 1.0** de 128 bits).
* **Estructura temporal:**
  1. **00:00 - 02:00 | Intro (Jose Fullscreen):** Por qué bajar a silicio abierto RISC-V cuando ya teníamos GPU Intel Arc y x86 AVX.
  2. **02:00 - 06:00 | Cross-Compiling sin dolor (`GOOS=linux GOARCH=riscv64`):**
     * Arquitectura heterogénea del Kendryte K230 (CPU0 800 MHz + CPU1 1.6 GHz con extensión vectorial `RVV 1.0`).
     * Compilar un binario estático Go con `GORISCV64=rva22u64` sin sufrir toolchains cruzados de C++.
  3. **06:00 - 11:00 | `12-riscv-rvv`: Ensamblador Vectorial RVV 1.0 en Go (Tarjeta Código + Terminal + Jose PiP):**
     * Comparativa directa entre `02/matrix_avx` (registros fijos `Y0..Y7` de 256 bits) y `12-riscv-rvv/vector_riscv64.s` (`VSETVLI`, `VLE32`, `VADDVV`, `VSE32` — longitud agnóstica).
     * Ejecución de la neurona vectorial e integración conceptual como sexto backend en `11-juego-final`.
  4. **11:00 - 14:30 | Dudas y Preguntas (Dúo Jose + Orbe Jarvis):**
     * **Jarvis:** ¿Qué diferencia al modelo *Vector Length Agnostic (VLA)* de RVV 1.0 frente al SIMD tradicional de x86 AVX?
     * **Jarvis:** ¿Por qué un binario estático de Go brilla en Edge AI RISC-V frente al footprint de Python?
  5. **14:30 - 15:00 | Cierre de Temporada (Jose Fullscreen):** Enlaces al repositorio `equilibristofgo/sandbox` y al blog.
