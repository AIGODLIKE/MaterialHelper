import os

import bpy


def import_material(name) -> "bpy.types.Material":
    folder = os.path.dirname(__file__)
    file_path = os.path.join(folder, "mat.blend")
    with bpy.data.libraries.load(str(file_path), link=False) as (data_from, data_to):
        data_to.materials = [name, ]
    return data_to.materials[0]
