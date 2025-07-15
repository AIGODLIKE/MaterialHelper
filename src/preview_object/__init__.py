import json
import lzma
import os
import time

import bpy
import numpy as np


def import_uv_to_mesh(mesh, data):
    uv = data["uv"]
    for key, value in uv.items():
        uv_layer = mesh.uv_layers.new(name=key)
        # uv_layer.data.foreach_set("uv", value)
        print("import_uv_to_mesh", key, value[:100])
        uv_layer.uv.foreach_set("vector", value)


def from_data_new_mesh(name, data) -> bpy.types.Mesh:
    mesh = bpy.data.meshes.new(name)
    verts_len = data["verts_len"]
    verts = data["verts"]
    faces = data["faces"]
    n_verts = np.array(verts, dtype=np.float16).reshape(verts_len, 3)
    mesh.from_pydata(n_verts, [], faces)
    import_uv_to_mesh(mesh, data)
    return mesh


def import_lzma_as_mesh(name):
    """
    dict_keys(['verts_len', 'verts', 'faces_len', 'faces', 'uv'])
    """
    folder = os.path.dirname(__file__)
    folder = r"C:\Development\Blender Addon\MaterialHelper\src\preview_object"
    file_name = f"{name}.lzma"

    file_path = os.path.join(folder, file_name)
    if not os.path.exists(file_path):
        file_path = os.path.join(folder, "SHADERBALL.lzma")

    with open(file_path, "rb+") as read_file:
        data = read_file.read()
        raw_data = lzma.decompress(data)
    data = json.loads(raw_data)

    print(data.keys())
    from_data_new_mesh(name, data)


if __name__ == "__main__":
    start_time = time.time()
    print("__file__", __file__)
    import_lzma_as_mesh("SHADERBALL")
    print("time", time.time() - start_time)
