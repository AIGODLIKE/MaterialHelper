import bpy

REFRESH_MATERIAL_LIST = []


def dprint(*args, end="\n"):
    from ..debug import DEBUG_EDIT_MATERIAL
    if DEBUG_EDIT_MATERIAL:
        print(*args, end=end)


def refresh_all():
    global REFRESH_MATERIAL_LIST
    if REFRESH_MATERIAL_LIST:
        while REFRESH_MATERIAL_LIST:
            item = REFRESH_MATERIAL_LIST.pop()
            refresh_material_asset_preview(item)


def refresh_material_asset_preview(name):
    """子进程刷新材质
    TIPS: 在关闭窗口时刷新会导致崩溃
    """
    dprint("start refresh_material_asset_preview", name)
    if name in bpy.data.materials:
        material = bpy.data.materials[name]
        dprint("material", material)
        # material.asset_generate_preview()
        dprint("asset_generate_preview", name)
        with bpy.context.temp_override(id=material):
            try:
                bpy.ops.ed.lib_id_generate_preview()
                dprint("lib_id_generate_preview", name)
            except RuntimeError:
                pass
    dprint("refresh_material_asset_preview", name)


def async_refresh_material(name):
    REFRESH_MATERIAL_LIST.append(name)
