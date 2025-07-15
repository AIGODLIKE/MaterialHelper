import json
import lzma
import os
import time

import bpy
import numpy as np

out_folder = folder = os.path.dirname(os.path.dirname(__file__))
start_time = time.time()


def get_mesh_data(mesh_obj) -> dict:
    mesh_data = {}
    np.set_printoptions(precision=3)
    vl = len(mesh_obj.data.vertices)
    v_data = np.zeros(vl * 3, dtype=np.float16)
    mesh_obj.data.vertices.foreach_get("co", v_data)
    mesh_data["verts_len"] = vl
    mesh_data["verts"] = list((round(float(v), 4) for v in v_data))
    faces = []
    for pol in mesh_obj.data.polygons:
        faces.append(list((v.real for v in pol.vertices)))
    mesh_data["faces_len"] = len(mesh_obj.data.polygons)
    mesh_data["faces"] = faces
    return mesh_data


def get_mesh_uv(mesh_obj):
    uv_data = {}
    for uv_layer in mesh_obj.data.uv_layers:
        ul = len(uv_layer.uv)
        v_data = np.zeros(ul * 2, dtype=np.float32)
        uv_layer.uv.foreach_get("vector", v_data)
        # for uv in uv_layer.uv:
        #     layer.append(tuple(round(i, 5) for i in uv.vector.to_tuple()))
        uv_data[uv_layer.name] = v_data.tolist()
        print("uv_data", mesh_obj.name, uv_layer.name, v_data[:100])
    return uv_data


for obj in bpy.context.scene.objects:
    st = time.time()
    data = get_mesh_data(obj)
    data["uv"] = get_mesh_uv(obj)
    ws = json.dumps(data, separators=(',', ':'))

    f = os.path.join(out_folder, f"{obj.name}.lzma")  # 压缩
    with open(f, "wb+") as wf:
        compressed_data = lzma.compress(ws.encode())
        wf.write(compressed_data)

    # w = os.path.join(folder, "py_data")  # 原数据
    # f = os.path.join(w, f"{obj.name}.json")
    # with open(f, "w+") as wf:
    #     wf.writelines(ws)
    print(obj.name, time.time() - st)

print("time", time.time() - start_time)
