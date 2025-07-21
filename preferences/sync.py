import bpy

from ..sync.material_to_asset import AssetSync


class Sync:
    # 用户总控制开关
    # bpy.types.Scene
    def update_material(self, context):
        print("update_material", self.auto_update)
        AssetSync.sync()

    auto_update: bpy.props.BoolProperty(
        name='Auto Update',
        default=True,
        description='If checked, the material will be automatically add as temp asset\nElse, temp assets will be cleared',
        update=update_material
    )

    # bpy.types.WindowManager
    sync_select: bpy.props.BoolProperty(
        name='Object / Material Select Sync',
        description="If checked, the active object's materials will be automatically selected",
        default=False)
