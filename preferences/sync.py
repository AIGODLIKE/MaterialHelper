import bpy
class Sync:
    # 用户总控制开关
    # bpy.types.Scene
    auto_update: bpy.props.BoolProperty(
        name='Auto Update',
        default=True,
        description='If checked, the material will be automatically add as temp asset\nElse, temp assets will be cleared',
    )

    # bpy.types.WindowManager
    update_active_obj_materials: bpy.props.BoolProperty(
        name='Object / Material Select Sync',
        description="If checked, the active object's materials will be automatically selected",
        default=False)
