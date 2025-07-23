import os

import bpy


def from_blend_import_mesh(name) -> bpy.types.Mesh:
    folder = os.path.dirname(__file__)
    file_path = os.path.join(folder, "shader_ball.blend")
    with bpy.data.libraries.load(str(file_path), link=False) as (data_from, data_to):
        data_to.meshes = [name, ]
    return data_to.meshes[0]


def from_blend_import_object(name) -> bpy.types.Object:
    folder = os.path.dirname(__file__)
    file_path = os.path.join(folder, "shader_ball.blend")
    with bpy.data.libraries.load(str(file_path), link=False) as (data_from, data_to):
        data_to.objects = [name, ]
    return data_to.objects[0]
