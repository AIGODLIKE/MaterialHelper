import bpy
import gpu
import numpy as np
from bpy.types import Operator
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
from gpu.types import Buffer
from mathutils import Vector


class RayCast(Operator):

    @staticmethod
    def get_gpu_buffer(xy, wh=(1, 1), centered=False) -> Buffer:
        """ 用于获取当前视图的GPU BUFFER
        :params xy: 获取的左下角坐标,带X 和Y信息
        :type xy: list or set
        :params wh: 获取的宽度和高度信息
        :type wh: list or set
        :params centered: 是否按中心获取BUFFER
        :type centered: bool
        :return bpy.gpu.Buffer: 返回活动的GPU BUFFER
        """

        if isinstance(wh, (int, float)):
            wh = (wh, wh)
        elif len(wh) < 2:
            wh = (wh[0], wh[0])

        x, y, w, h = int(xy[0]), int(xy[1]), int(wh[0]), int(wh[1])
        if centered:
            x -= w // 2
            y -= h // 2

        depth_buffer = gpu.state.active_framebuffer_get().read_depth(x, y, w, h)
        return depth_buffer

    @classmethod
    def gpu_depth_ray_cast(cls, x, y, data) -> None:
        size = 10  # ray cast pixels

        buffer = cls.get_gpu_buffer([x, y], wh=[size, size], centered=True)
        numpy_buffer = np.asarray(buffer, dtype=np.float32).ravel()
        min_depth = np.min(numpy_buffer)
        data['is_in_model'] = (min_depth != (0 or 1))

    def get_mouse_location_ray_cast(self, context, event) -> bool:
        x, y = (event.mouse_region_x, event.mouse_region_y)
        view3d = context.space_data
        show_xray = view3d.shading.show_xray
        view3d.shading.show_xray = False
        data = {}
        sp = bpy.types.SpaceView3D
        han = sp.draw_handler_add(self.gpu_depth_ray_cast,
                                  (x, y, data), 'WINDOW',
                                  'POST_PIXEL')
        bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
        sp.draw_handler_remove(han, 'WINDOW')
        view3d.shading.show_xray = show_xray
        return data['is_in_model']


def mouse_2d_ray_cast(context: bpy.types.Context, mouse: Vector):
    """
    通过鼠标位置和当前视图获取鼠标所在位置的ray_cast
    Args:
        context:
        mouse:

    Returns:
        result, location, normal, index, object, matrix
    """
    scene = context.scene
    region = context.region
    region_data = context.region_data
    depsgraph = context.evaluated_depsgraph_get()
    origin = region_2d_to_origin_3d(region, region_data, mouse)
    direction = region_2d_to_vector_3d(region, region_data, mouse)
    return scene.ray_cast(depsgraph=depsgraph, origin=origin, direction=direction)


def object_ray_cast(obj, context, mouse):
    region = context.region
    region_data = context.region_data
    depsgraph = context.evaluated_depsgraph_get()
    origin = region_2d_to_origin_3d(region, region_data, mouse)
    direction = region_2d_to_vector_3d(region, region_data, mouse)
    return obj.ray_cast(depsgraph=depsgraph, origin=origin, direction=direction)


def mouse_2d_ray_cast_by_mouse_area(context: bpy.types.Context, event: bpy.types.Event):
    from .area import find_mouse_in_area
    area = find_mouse_in_area(context, event)
    res = False, None, None, None, None, None
    if area is None:
        return res

    regions = [region for region in area.regions if region.type == "WINDOW"]
    if len(regions) == 0:
        return res

    mouse = Vector((event.mouse_x, event.mouse_y)) - Vector((area.x, area.y))

    scene = context.scene
    region = regions[0]
    spaces = [space for space in area.spaces if space.type == "VIEW_3D"]
    if len(spaces) == 0:
        return res
    region_data = spaces[0].region_3d
    depsgraph = context.evaluated_depsgraph_get()
    origin = region_2d_to_origin_3d(region, region_data, mouse)
    direction = region_2d_to_vector_3d(region, region_data, mouse)
    return scene.ray_cast(depsgraph=depsgraph, origin=origin, direction=direction)
