import bpy
from mathutils import Vector


def get_area_max_parent(area: bpy.types.Area):
    """如果当前area是最大化的
    则反回未最大化之前的area
    pixels.foreach_set"""
    screen = bpy.context.screen
    if screen.show_fullscreen:
        if bpy.context.screen.name.endswith("-nonnormal"):  # 当前屏幕为最大化时，获取最大化之前的屏幕
            name = screen.name.replace("-nonnormal", "")
            screen = bpy.data.screens.get(name, None)
            if screen:
                for i in screen.areas:
                    if i.type == "EMPTY":
                        return i
    return area


def find_mouse_in_area(context, event) -> "bpy.types.Area|None":
    """查找在鼠标上的区域
    就是鼠标活动区域
    """
    mouse = Vector((event.mouse_x, event.mouse_y)).freeze()
    for area in context.screen.areas:
        xy = Vector((area.x, area.y)).freeze()
        aw = xy + Vector((area.width, area.height)).freeze()
        if xy.x < mouse.x < aw.x and xy.y < mouse.y < aw.y:
            return area
    return None

