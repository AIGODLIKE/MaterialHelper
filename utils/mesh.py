from time import time

import bpy
import numpy as np


def _get_mesh(data: object):
    """获取物体网格数据,可直接输入物体或是网格
    如果不是网格物体则会反回错误

    """
    if type(data) == bpy.types.Mesh:
        data.update()
        obj = data
    elif (type(data) == bpy.types.Object) and (data.type == "MESH"):
        data.update_from_editmode()
        obj = data.data
    else:
        obj = Exception(f"物体{data}不是一个网格物体")
    return obj


def vertices_co(data, *, matrix=None, debug=False):
    """从object.data获取物体的顶点坐标并反回numpy数据
    Args:
        data (_bpy.types.Object, _bpy.data.meshes):输入一个网格或物体
        matrix (bool):输入一个矩阵用于点乘每一个点,如果不输入则不进行点乘操作
        debug (bool):打印获取数据的时间,计算将会消耗一些性能
    Returns:
        numpy.array: 反回所有顶点坐标的np阵列
    """
    from .math import np_matrix_dot

    st = time()
    try:
        data = _get_mesh(data)
        vertices = data.vertices
        v_l = vertices.__len__()
        np_co = np.zeros(v_l * 3, dtype=np.float32)

        vertices.foreach_get("co", np_co)
    except Exception as e:
        print(f"获取错误:{data} 不是有效的网格或物体数据 {e.args}")

    else:
        np_co = np_co.reshape((v_l, 3))

        if matrix:
            np_co = np_matrix_dot(np_co, matrix)
        if debug:
            print(f"获取{data}顶点数据,共用时{time() - st}s")
        return np_co


def from_face_index_get_material_index(obj, face_index) -> "int":
    import bmesh

    assert obj and obj.type == "MESH", "必须是网格"

    material_index = -1
    try:
        if obj.mode == "EDIT":
            bm = bmesh.from_edit_mesh(obj.data)
        else:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        material_index = bm.faces[face_index].material_index
    except IndexError as e:
        # levels = get_object_subdivision_level(obj)
        # fl = len(bm.faces)
        # while levels != 0:
        #     material_index /= 4
        #     levels -= 1
        # # material_index = face_index ** (-levels)
        # # material_index = int(material_index)
        # sub_l = fl ** levels
        # face_index / sub_l
        # print("from_face_index_get_material_index", material_index, obj.name, face_index, e)
        ...
    bm.free()
    return material_index


def from_face_index_get_material(obj, face_index) -> "bpy.types.Material|None":
    """bpy.data.meshes["苏珊娜.005"].polygons[0].material_index"""
    material_index = from_face_index_get_material_index(obj, face_index)
    try:
        return obj.material_slots[material_index].material
    except IndexError:
        return None
