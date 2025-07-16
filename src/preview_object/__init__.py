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
        uv_layer.uv.foreach_set("vector", value)


def from_data_new_mesh(name, data) -> bpy.types.Mesh:
    mesh = bpy.data.meshes.new(name)
    verts_len = data["verts_len"]
    verts = data["verts"]
    faces = data["faces"]
    vertex_normals = data["vertex_normals"]
    n_verts = np.array(verts, dtype=np.float16).reshape(verts_len, 3)
    mesh.from_pydata(n_verts, [], faces)
    mesh.vertex_normals.foreach_set("vector", vertex_normals)
    import_uv_to_mesh(mesh, data)
    return mesh


def lzma_import_as_mesh(name) -> bpy.types.Mesh:
    """
    通过lzma压缩的网格数据
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
    return from_data_new_mesh(name, data)


if __name__ == "__main__":
    start_time = time.time()
    print("__file__", __file__)
    lzma_import_as_mesh("SHADERBALL")
    print("time", time.time() - start_time)
