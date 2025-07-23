import os

import bpy

materials_list = []


def get_all_material():
    global materials_list

    if len(materials_list) == 0:
        folder = os.path.dirname(__file__)
        file_path = os.path.join(folder, "mat.blend")
        with bpy.data.libraries.load(str(file_path), link=False) as (data_from, data_to):
            materials_list.extend(data_from.materials[:])
    return materials_list


def import_material(name) -> "bpy.types.Material":
    folder = os.path.dirname(__file__)
    file_path = os.path.join(folder, "mat.blend")
    with bpy.data.libraries.load(str(file_path), link=False) as (data_from, data_to):
        data_to.materials = [name, ]
    return data_to.materials[0]
