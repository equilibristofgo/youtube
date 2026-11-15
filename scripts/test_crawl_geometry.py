import bpy
import math
import os

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.fps = 25
scene.frame_start = 1
scene.frame_end = 100

# World: Space with starry background
world = bpy.data.worlds.new("StarField")
scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

bg_node = nodes.new(type="ShaderNodeBackground")
bg_node.inputs["Color"].default_value = (0.005, 0.008, 0.02, 1.0)
bg_node.inputs["Strength"].default_value = 1.0

# Procedural stars
tex_coord = nodes.new(type="ShaderNodeTexCoord")
voronoi = nodes.new(type="ShaderNodeTexVoronoi")
voronoi.feature = 'F1'
voronoi.inputs["Scale"].default_value = 180.0

ramp = nodes.new(type="ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.06
ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
ramp.color_ramp.elements[1].position = 0.075
ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

add_node = nodes.new(type="ShaderNodeAddShader")
star_bg = nodes.new(type="ShaderNodeBackground")
star_bg.inputs["Strength"].default_value = 3.0

out_node = nodes.new(type="ShaderNodeOutputWorld")

links.new(tex_coord.outputs["Generated"], voronoi.inputs["Vector"])
links.new(voronoi.outputs["Distance"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], star_bg.inputs["Color"])
links.new(bg_node.outputs["Background"], add_node.inputs[0])
links.new(star_bg.outputs["Background"], add_node.inputs[1])
links.new(add_node.outputs["Shader"], out_node.inputs["Surface"])

# Camera setup: 28mm wide lens, tilted 62 degrees
cam_data = bpy.data.cameras.new("StarCam")
cam_data.lens = 28
cam_data.clip_end = 150
cam_obj = bpy.data.objects.new("StarCam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0.0, -3.2, 1.9)
cam_obj.rotation_euler = (math.radians(62.0), 0.0, 0.0)

# Text on the ground plane (Z=0, lying flat, facing +Z)
text_data = bpy.data.curves.new(name="CrawlData", type='FONT')
text_data.body = """EPISODIO TOTAL

LA REBELION DEL SILICIO LIBRE

La galaxia del Machine Learning ha caido bajo el yugo
del Imperio de x86 y las tarjetas de cuarenta mil dolares.

Pero en los confines del codigo abierto, una pequena alianza
de ingenieros y gophers ha comenzado una revolucion.
Su arma: el lenguaje Go y la arquitectura RISC-V.

Este documental de una hora es una cronica viva en collage:
las primeras partes exploran el dolor de los tensores a mano,
y las tres siguientes el asalto final al procesador Kendryte K230."""

text_data.align_x = 'CENTER'
text_data.align_y = 'TOP'
text_data.size = 0.38
text_data.space_line = 1.45

text_obj = bpy.data.objects.new("CrawlObj", text_data)
scene.collection.objects.link(text_obj)
text_obj.rotation_euler = (0.0, 0.0, 0.0)

# Material with distance fade (Y gradient)
mat = bpy.data.materials.new("StarWarsTextMat")
mat.use_nodes = True
mat.blend_method = 'BLEND'
m_nodes = mat.node_tree.nodes
m_links = mat.node_tree.links
m_nodes.clear()

m_out = m_nodes.new(type="ShaderNodeOutputMaterial")
m_bsdf = m_nodes.new(type="ShaderNodeBsdfPrincipled")
m_bsdf.inputs["Base Color"].default_value = (1.0, 0.88, 0.12, 1.0)
m_bsdf.inputs["Emission Color"].default_value = (1.0, 0.88, 0.12, 1.0)
m_bsdf.inputs["Emission Strength"].default_value = 1.0

# Distance fade along world Y
geom = m_nodes.new(type="ShaderNodeNewGeometry")
sep = m_nodes.new(type="ShaderNodeSeparateXYZ")
fade_ramp = m_nodes.new(type="ShaderNodeValToRGB")
# Fade out between Y = 3.0 and Y = 8.5
fade_ramp.color_ramp.elements[0].position = 0.25 # near: alpha 1.0
fade_ramp.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)
fade_ramp.color_ramp.elements[1].position = 0.70 # far: alpha 0.0
fade_ramp.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)

# Map range for Y coordinate
map_r = m_nodes.new(type="ShaderNodeMapRange")
map_r.inputs["From Min"].default_value = 0.0
map_r.inputs["From Max"].default_value = 10.0
map_r.inputs["To Min"].default_value = 0.0
map_r.inputs["To Max"].default_value = 1.0

m_links.new(geom.outputs["Position"], sep.inputs["Vector"])
m_links.new(sep.outputs["Y"], map_r.inputs["Value"])
m_links.new(map_r.outputs["Result"], fade_ramp.inputs["Fac"])
m_links.new(fade_ramp.outputs["Color"], m_bsdf.inputs["Alpha"])
m_links.new(m_bsdf.outputs["BSDF"], m_out.inputs["Surface"])

text_data.materials.append(mat)

# Position text midway to test perspective
text_obj.location = (0.0, 1.8, 0.0)

scene.render.filepath = "/home/jose/workspace/equilibristofgo/youtube/clips/test_crawl_frame.png"
bpy.ops.render.render(write_still=True)
print("[✓] Frame rendered successfully!")
