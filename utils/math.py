from math import pi

import bpy
import numpy as np
from mathutils import Vector, Matrix, Euler


def np_matrix_dot(np_co, matrix):
    np_co = np.insert(np_co, 3, 1, axis=1).T  # 对numpy数据插入一位数并进行转置
    np_co[:] = np.dot(matrix, np_co)  # 点乘得到变换后的点位置
    np_co /= np_co[3, :]  # 除一下第四位
    np_co = np_co.T  # 再转置一下
    np_co = np_co[:, :3]  # 取前三位坐标数据
    return np_co


def location_to_matrix(location: Vector) -> Matrix:
    return Matrix.Translation(location)


def rotation_to_matrix(rotation: Euler) -> Matrix:
    return rotation.to_matrix().to_4x4()


def scale_to_matrix(scale: Vector) -> Matrix:
    matrix = Matrix()
    for i in range(3):
        matrix[i][i] = scale[i]
    return matrix


def normal_to_rotation_matrix(normal: Vector, target_direction=Vector((0, 0, 1))) -> Matrix:
    """法向转换为旋转矩阵
    只能确定一个方向
    """
    # 计算旋转矩阵
    rotation_matrix = target_direction.rotation_difference(normal).to_matrix()

    # 将旋转矩阵转换为四元数
    rotation_quaternion = rotation_matrix.to_quaternion()
    return rotation_quaternion.to_matrix().to_4x4()


def print_matrix(matrix):
    print(f"{matrix.__repr__()}")


def check_tow_direction_vector_perpendicular(a, b):
    """判断两个方向矢量是否平行
    反回是否平行的布尔值

    e.g.
    a = Vector((1,0,0))
    b = Vector((-1,0,0))
    (pi - a.angle(b)) > 0.001
    True

    a = Vector((1, 0, 0.1))
    b = Vector((-1, 0, 0))
    (pi - a.angle(b)) > 0.001
    False
    """
    return not ((pi - a.angle(b)) > 0.001)


def find_max_difference(num_list):
    """查找列表中和其它值相差最大的值
    通过排序
    """
    if len(num_list) <= 1:
        return None
    num_list.sort()
    diff_start = abs(num_list[1] - num_list[0])
    diff_end = abs(num_list[-1] - num_list[-2])
    if diff_start > diff_end:
        return num_list[0]
    return num_list[-1]


def from_x_z_vector_get_matrix(x, z) -> Matrix:
    """从两个矢量获取旋转矩阵"""
    import mathutils

    # 定义两个3D向量
    y = z.cross(x)
    y.normalize()
    z.normalize()
    x = y.cross(z)
    x.normalize()
    # 生成旋转矩阵
    rot_matrix = mathutils.Matrix.Identity(4)
    rot_matrix.col[0][:3] = x
    rot_matrix.col[1][:3] = y
    rot_matrix.col[2][:3] = z
    return rot_matrix


def from_edit_bone_get_matrix(obj: bpy.types.Object, bone: bpy.types.Bone) -> Matrix:
    """从编辑骨格获取Matrix"""
    om = obj.matrix_world.copy()
    rot = rotation_to_matrix(bone.matrix.to_euler())
    if bone.select:
        loc = bone.center
    elif bone.select_tail:
        loc = bone.tail
    elif bone.select_head:
        loc = bone.head
    else:
        loc = bone.center
    return om @ (location_to_matrix(loc) @ rot)


def from_pose_bone_get_matrix(obj: bpy.types.Object, bone: bpy.types.Bone) -> Matrix:
    """从骨格姿势模式获取Matrix
    TODO 子骨骼的方向需要对齐
    """
    om = obj.matrix_world.copy()
    rot = rotation_to_matrix(bone.matrix.to_euler())

    if bone.parent:
        parent_tail_loc = location_to_matrix(bone.parent.tail_local)
        return om @ (parent_tail_loc @ bone.matrix.to_4x4() @ rot)
    return om @ (location_to_matrix(bone.head)) @ rot


def from_curve_get_matrix(obj: bpy.types.Object, curve: bpy.types.Curve) -> Matrix:
    select_count = 0
    loc = Vector()
    rot = rotation_to_matrix(obj.matrix_world.to_euler())

    for spline in curve.splines:
        for p in spline.points:
            if p.select:
                select_count += 1
                loc += p.co.to_3d()  # point.co is 4d data
        for bp in spline.bezier_points:
            if bp.select_control_point:
                select_count += 1
                loc += bp.co

    if select_count != 0:
        loc /= select_count

    loc = obj.matrix_world @ loc
    return location_to_matrix(loc) @ rot


def is_even(number) -> bool:
    """判断是否为偶数"""
    return (number % 2) == 0
