import bpy


class Sync:
    auto_update: bpy.props.BoolProperty(
        name='Auto Update',
        default=True,
        description='If checked, the material will be automatically add as temp asset\nElse, temp assets will be cleared',
    )

    sync_select: bpy.props.BoolProperty(
        name='Select Sync',
        description="If checked, the active object's materials will be automatically selected",
        default=False)
