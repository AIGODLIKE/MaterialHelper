import math
from functools import cache

import bpy
import gpu
import numpy as np
from gpu.types import GPUTexture
from gpu_extras.batch import batch_for_shader


def from_material_get_texture_by_image(material: bpy.types.Material) -> gpu.types.GPUTexture:
    """
    ("RGBA8UI", "RGBA8I", "RGBA8", "RGBA32UI", "RGBA32I", "RGBA32F", "RGBA16UI", "RGBA16I",
    "RGBA16F", "RGBA16", "RG8UI", "RG8I", "RG8", "RG32UI", "RG32I", "RG32F", "RG16UI",
    "RG16I", "RG16F", "RG16", "R8UI", "R8I", "R8", "R32UI", "R32I", "R32F", "R16UI",
    "R16I", "R16F", "R16", "R11F_G11F_B10F", "DEPTH32F_STENCIL8", "DEPTH24_STENCIL8",
    "SRGB8_A8", "RGB16F", "SRGB8_A8_DXT1", "SRGB8_A8_DXT3", "SRGB8_A8_DXT5", "RGBA8_DXT1",
    "RGBA8_DXT3", "RGBA8_DXT5", "DEPTH_COMPONENT32F", "DEPTH_COMPONENT24", "DEPTH_COMPONENT16"
    """
    preview = material.preview
    w, h = preview.icon_size[:]
    image = bpy.data.images.new(material.name, w, h, alpha=True)
    image.pixels[:] = preview.icon_pixels_float[:]
    texture = gpu.texture.from_image(image)
    bpy.data.images.remove(image)  # 在删除图片时资产页面会刷新
    return texture


def from_material_get_gpu_texture_by_pixel(material: bpy.types.Material) -> gpu.types.GPUTexture | None:
    from .color import srgb_to_linear
    w, h = material.preview.icon_size[:]
    size = w * h * 4
    flow_data = np.zeros(size, dtype=np.float32)
    material.preview_ensure().icon_pixels_float.foreach_get(flow_data)
    flow_data = srgb_to_linear(flow_data)
    try:
        buffer = gpu.types.Buffer("FLOAT", (w, h, 4), flow_data.reshape((w, h, 4)))
        texture = gpu.types.GPUTexture((w, h), format="RGBA16F", data=buffer)
        return texture
    except AttributeError:
        return None


def from_file_get_texture(file_path: str) -> gpu.types.GPUTexture:
    image = bpy.data.images.load(filepath=file_path, check_existing=True)
    texture = gpu.texture.from_image(image)
    bpy.data.images.remove(image)
    return texture


def draw_2d_texture(texture, w, h, scale=1) -> None:
    dw, dh = w * scale, h * scale
    shader = gpu.shader.from_builtin("IMAGE_COLOR")
    batch = batch_for_shader(
        shader, "TRI_FAN",
        {
            "pos": ((0, 0), (dw, 0), (dw, dh), (0, dh)),
            "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
        },
    )
    shader.uniform_sampler("image", texture)
    shader.bind()
    batch.draw(shader)


def draw_box(a, b, color=(.5, .5, .5, 1)):
    indices = ((0, 1, 2), (2, 1, 3))

    x1, y1 = a
    x2, y2 = b
    vertices = ((x1, y1), (x2, y1), (x1, y2), (x2, y2))
    # draw area
    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    batch = batch_for_shader(shader,
                             "TRIS", {"pos": vertices},
                             indices=indices)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


@cache
def get_rounded_rectangle_vertex(radius=10, width=200, height=200, segments=10) -> tuple:
    if segments <= 0:
        raise ValueError("Amount of segments must be greater than 0.")
    w = int((width - radius) / 2) - radius / 2
    h = int((height - radius) / 2) - radius / 2
    # 角度步长，通常以度为单位
    # 存储顶点坐标的列表
    vertex = []
    quadrant = [
        (w, h),
        (-w, h),
        (-w, -h),
        (w, -h),
    ]
    angle_step = 360 / (segments * 4)  # 这里选择了8个顶点，可以根据需要调整

    def qa(qq, a):
        x = qq[0] + radius * math.cos(a)
        y = qq[1] + radius * math.sin(a)
        vertex.append((x, y))

    # 计算顶点坐标
    angle = None
    for i in range(4):
        for j in range(segments):
            index = segments * i + j
            angle = math.radians(index * angle_step)  # 将角度转换为弧度
            qa(quadrant[i], angle)
        qa(quadrant[(i + 1) % 4], angle)
    qa(quadrant[3], angle)
    qa(quadrant[3], 0)
    return tuple(vertex)


@cache
def get_indices_from_vertex(vertex):
    indices = []
    for i in range(len(vertex) - 2):
        indices.append((0, i + 1, i + 2))
    return indices


def draw_rounded_rectangle_area(color=(1, 1, 1, 1.0), *, radius=15, width=200, height=200,
                                segments=64):
    vertex = get_rounded_rectangle_vertex(radius, width, height, segments)
    indices = get_indices_from_vertex(vertex)
    shader = gpu.shader.from_builtin("SMOOTH_COLOR")
    batch = batch_for_shader(shader,
                             "TRIS",
                             {"pos": vertex, "color": [color for _ in range(len(vertex))]},
                             indices=indices)
    batch.draw(shader)
