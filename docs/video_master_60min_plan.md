# Plan y Packaging del Vídeo Maestro (1 Hora): La Rebelión del Silicio Libre

## 1. Título Oficial y Subtítulos Virales

### Título Principal (Recomendado):
```text
El Fin del Monopolio de NVIDIA y x86: Creamos una Inteligencia Artificial en Silicio Libre RISC-V con Go (1 Hora)
```

### Subtítulos Alternativos (para Descripción, Shorts y Posts):
* **El gancho geopolítico:** *La Guerra de los Chips: ¿Por qué China apuesta todo a RISC-V? (Y cómo programamos una IA en Silicio Abierto con Go)*
* **El gancho hacker:** *Sin Python, Sin CUDA, Sin x86: De las Matemáticas al Chip Chino K230*
* **El enfoque Masterclass:** *De Tensores Manuales a RVV 1.0 en Kendryte K230: 1 Hora de Machine Learning en Go*

---

## 2. Disclaimer Inicial: "Star Wars Opening Crawl" (Prólogo del Collage)

Para dar coherencia narrativa al cambio de formatos (las 2 primeras sesiones fueron directos con LiveKit y las 3 últimas producción automatizada con avatares en GPU Intel Arc), el vídeo arrancará con un prólogo galáctico en perspectiva 3D sobre fondo de estrellas:

```text
EPISODIO TOTAL: LA REBELIÓN DEL SILICIO LIBRE

Hace no mucho tiempo, en una estación de trabajo no tan lejana...

La galaxia del Machine Learning ha caído bajo el yugo del Imperio de x86,
las tarjetas gráficas de cuarenta mil dólares de NVIDIA y los gigantescos
contenedores de Python que devoran decenas de gigabytes de memoria.

Pero en los confines del código abierto, una pequeña alianza de ingenieros
y gophers ha comenzado una revolución silenciosa. Su arma: el lenguaje Go,
la concurrencia nativa y la arquitectura de silicio libre RISC-V.

Este documental de una hora es una crónica viva de dicha travesía técnica.
Una obra en collage que une dos épocas de producción:

Las dos primeras partes fueron grabadas en directo con agentes interactivos
de LiveKit, explorando el dolor de los tensores artesanales y el salto
a las librerías profesionales con Gonum.

Las tres partes restantes fueron forjadas con un pipeline autónomo
acelerado por GPU Intel Arc, donde los modelos cobran vida a 60 FPS en el
motor Ebiten, y el copiloto holográfico Jarvis acompaña a Jose en el
asalto final a la placa Kendryte K230 mediante ensamblador vectorial RVV 1.0.

Ajustad vuestros compiladores y preparaos para el salto hiperespacial:
del cálculo matricial elemental al silicio libre...
```

---

## 3. Descripción Oficial para YouTube

```text
¿Es posible crear una Inteligencia Artificial completa desde cero sin tocar Python, sin depender de librerías CUDA de NVIDIA y ejecutándola sobre silicio libre en un procesador RISC-V de bajo consumo?

En este documental técnico de 1 hora ("Equilibristas de Golang"), rompemos el monopolio de las arquitecturas privativas (x86 y ARM) y las nubes multimillonarias. A lo largo de cinco bloques en formato collage —desde directos de investigación en LiveKit hasta simulaciones visuales a 60 FPS y ensamblador vectorial puro— construimos una red neuronal paso a paso en el lenguaje Go y la llevamos hasta la placa CanMV-K230 (SoC Kendryte K230 Dual-Core RISC-V T-Head C908 con unidad vectorial RVV 1.0).

---

🔥 SUBTÍTULOS Y TEMÁTICAS CLAVE:
• La Guerra de los Chips: ¿Por qué China apuesta todo a RISC-V frente al veto de ASML y EE.UU.?
• Sin Python ni CUDA: Compilando binarios estáticos de 1.4 MB para Linux embebido.
• Filosofía Vector Length Agnostic (VLA): Por qué RVV 1.0 supera a AVX-256 y AVX-512.
• Simulación a 60 FPS: Deformando el tejido cósmico (Deep Space) para entender la Hipótesis del Manifold.

---

⏱️ TIMESTAMPS / CAPÍTULOS:
00:00 - Prólogo Galáctico: La Rebelión del Silicio Libre
01:18 - PARTE 1: Cimientos y Concurrencia (Goroutines, Worker Pools y Tensores Manuales en Go)
16:52 - PARTE 2: El Dolor del Escalado y Gonum (Multiplicación Matricial y GPU Intel Arc)
34:22 - PARTE 3: Anatomía Visual del Aprendizaje (XOR, Backpropagation y Geometría de Peso vs Sesgo)
43:35 - PARTE 4: La Vida en Tiempo Real a 60 FPS (Ebiten, Manifold Cósmico y WebAssembly)
51:17 - PARTE 5: Del Cloud al Silicio Libre (Arquitectura Kendryte K230 y Ensamblador RVV 1.0)

---

🛠️ RECURSOS, BLOG Y COMUNIDAD:
• Entrada completa en el Blog (Desglose técnico de las 5 partes y pipeline autónomo):
  https://equilibristofgo.github.io/blog/posts/04-post/
• ¿Quieres participar o apuntarte a la comunidad? Lee antes nuestras normas:
  https://github.com/equilibristofgo/blog/blob/main/CODE_OF_CONDUCT.md
• Manifiesto "¿De qué va esto?": Cómo unirse a los debates de Equilibristas de Golang:
  https://equilibristofgo.github.io/blog/posts/00-de-que-va-esto/
• Repositorio completo (Simuladores Ebiten + Ensamblador RISC-V):
  https://github.com/equilibristofgo/sandbox
• Curso original NYU Deep Learning (Yann LeCun & Alfredo Canziani):
  https://atcold.github.io/NYU-DLSP20/

---

💻 HARDWARE Y SOFTWARE UTILIZADO:
• GPU: Intel Arc B580 (12 GB VRAM) — PyTorch XPU / Level Zero / SadTalker
• Placa Edge AI: CanMV-K230 (SoC Canaan Kendryte K230, T-Head C908 Dual-Core 1.6 GHz + RVV 1.0 128-bit)
• Motores TTS: Kokoro-TTS (OpenVINO / CPU)
• Lenguaje: Go 1.24 (con ensamblador Plan 9 para riscv64)

#riscv #golang #machinelearning #guerradeloschips #deeplearning #china #kendryte #ebiten #webassembly #siliciolibre #intelarc #hardwarelibre
```

---

## 4. Estrategia de Concatenación Técnica

Para ensamblar los 5 episodios con transiciones suaves sin pérdida de calidad:
1. **Prólogo Star Wars (`prologo_star_wars.mp4`):** Generar vídeo 1080p de 75 segundos con música o ambientación sutil de espacio y texto inclinado en perspectiva.
2. **Normalización de Formatos:**
   * Sesión 1 (`640x360 @ 30fps`) y Sesión 2 (`640x360 @ 30fps`): Reescalado bicúbico limpio a 1080p con padding / marco de estudio o estirado manteniendo aspect ratio 16:9 y audio a 48 kHz estéreo.
   * Sesión 3, 4 y 5: Ya están renderizados nativamente a `1920x1080 @ 25fps` con audio AAC 48 kHz.
3. **Cartelas de Capítulo:** Un separador elegante de 3 segundos entre cada parte ("PARTE 1 // CIMIENTOS", "PARTE 2 // GONUM", etc.).
4. **Montaje:** En Blender VSE o FFmpeg concat demuxer con reencodificado H.264 CRF 20 a 1080p constante.

