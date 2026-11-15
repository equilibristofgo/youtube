#!/usr/bin/env python3
"""
generar_crawl_star_wars.py

Genera un prólogo espacial animado estilo Star Wars en 3D usando Blender headless.
Crea la mítica perspectiva inclinada desvaneciéndose en las estrellas.
"""

import math
import os
import sys
import bpy

OUTPUT_PATH = sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-1].endswith(".mp4") else "clips/prologo_star_wars.mp4"
DURATION_SEC = 60
FPS = 25
TOTAL_FRAMES = DURATION_SEC * FPS

CRAWL_TEXT = """EPISODIO TOTAL: LA REBELIÓN DEL SILICIO LIBRE

Hace no mucho tiempo, en una estación de trabajo no tan lejana...

La galaxia del Machine Learning ha caído bajo el yugo del
Imperio de x86, las tarjetas gráficas de cuarenta mil dólares
de NVIDIA y los gigantescos contenedores de Python que devoran
decenas de gigabytes de memoria.

Pero en los confines del código abierto, una pequeña alianza
de ingenieros y gophers ha comenzado una revolución silenciosa.
Su arma: el lenguaje Go, la concurrencia nativa y la arquitectura
de silicio libre RISC-V.

Este documental de una hora es una crónica viva de dicha travesía:
un collage técnico que une dos épocas de producción.

Las dos primeras partes fueron grabadas en directo mediante agentes
interactivos de LiveKit, explorando el dolor de los tensores artesanales
y el salto al álgebra profesional con Gonum.

Las tres partes restantes fueron forjadas con un pipeline autónomo
acelerado por GPU Intel Arc, donde los modelos cobran vida a 60 FPS
en el motor Ebiten, y el copiloto holográfico Jarvis acompaña a Jose
en el asalto final a la placa Kendryte K230 mediante ensamblador
vectorial RVV 1.0.

Ajustad vuestros compiladores y preparaos para el salto hiperespacial:
del cálculo matricial elemental al silicio abierto..."""


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = TOTAL_FRAMES

    # Color management
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'

    # Mundo espacial oscuro con estrellas
    world = bpy.data.worlds.new("StarWorld")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.01, 0.015, 0.03, 1.0)

    # Cámara inclinada mirando hacia adelante y arriba
    cam_data = bpy.data.cameras.new("CrawlCam")
    cam_data.lens = 35
    cam_data.clip_end = 200
    cam_obj = bpy.data.objects.new("CrawlCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0.0, -9.0, 3.2)
    cam_obj.rotation_euler = (math.radians(68.0), 0.0, 0.0)

    # Objeto de Texto 3D
    text_data = bpy.data.curves.new(name="CrawlTextData", type='FONT')
    text_data.body = CRAWL_TEXT
    text_data.align_x = 'CENTER'
    text_data.align_y = 'TOP'
    text_data.size = 0.52
    text_data.space_line = 1.35
    text_data.extrude = 0.01

    text_obj = bpy.data.objects.new("CrawlText", text_data)
    scene.collection.objects.link(text_obj)
    text_obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)

    # Material amarillo Star Wars (#FFE81F -> sRGB ~ 1.0, 0.91, 0.12)
    mat = bpy.data.materials.new(name="StarWarsYellow")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (1.0, 0.85, 0.10, 1.0)
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (1.0, 0.85, 0.10, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 0.8
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (1.0, 0.85, 0.10, 1.0)
    text_data.materials.append(mat)

    # Animación de desplazamiento vertical (eje Y / Z)
    # Comienza debajo del encuadre y asciende hacia la lejanía
    start_y = -6.0
    end_y = 28.0

    text_obj.location = (0.0, start_y, -1.5)
    text_obj.keyframe_insert(data_path="location", frame=1)

    text_obj.location = (0.0, end_y, -1.5)
    text_obj.keyframe_insert(data_path="location", frame=TOTAL_FRAMES)

    # Hacer interpolación lineal pura para velocidad constante
    if text_obj.animation_data and text_obj.animation_data.action:
        for fcurve in text_obj.animation_data.action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'

    # Render config
    os.makedirs(os.path.dirname(os.path.abspath(OUTPUT_PATH)), exist_ok=True)
    scene.render.filepath = os.path.abspath(OUTPUT_PATH)
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') else 'BLENDER_WORKBENCH'

    print(f"[*] Escena lista: {TOTAL_FRAMES} frames ({DURATION_SEC}s) -> {OUTPUT_PATH}")
    bpy.ops.render.render(animation=True)
    print(f"[✓] Vídeo Star Wars Crawl generado con éxito: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_scene()

