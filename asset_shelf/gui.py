import bpy
from bpy.types import (
    AssetHandle,
    AssetRepresentation,
    Context,
    Menu,
    Panel,
    UILayout,
    UIList,
    WindowManager,
    WorkSpace,
)
from pathlib import Path
from bl_ui_utils.layout import operator_context


class MATHP_AST_asset_library(bpy.types.AssetShelf):
    bl_space_type = "VIEW_3D"
    show_names = True

    # We have own keymap items to add custom drag behavior (pose blending), disable the default
    # asset dragging.
    # bl_options = {'NO_ASSET_DRAG'}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return True

    @classmethod
    def asset_poll(cls, asset: AssetRepresentation) -> bool:
        # return asset.id_type == 'NODETREE'
        return asset.id_type == 'MATERIAL'

    @classmethod
    def draw_context_menu(cls, _context: Context, _asset: AssetRepresentation, layout: UILayout):
        asset_dis = _context.asset
        blend_path = asset_dis.full_library_path
        asset_name = asset_dis.name
        asset_dir = Path(blend_path).parent

        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.operator(MATHP_OT_refresh_preview.bl_idname)


class MATHP_OT_refresh_preview(bpy.types.Operator):
    bl_idname = 'mathp.refresh_preview'
    bl_label = 'Refresh'

    def execute(self, context):
        import bpy
        a = context.area
        regions = [r for r in a.regions if r.type == 'ASSET_SHELF']
        if regions:
            with bpy.context.temp_override(area=a, region=regions[0]):
                bpy.ops.asset.library_refresh()

        return {'FINISHED'}


### Messagebus subscription to monitor asset library changes.
_msgbus_owner = object()


def register():
    bpy.utils.register_class(MATHP_AST_asset_library)
    bpy.utils.register_class(MATHP_OT_refresh_preview)


def unregister():
    bpy.utils.unregister_class(MATHP_AST_asset_library)
    bpy.utils.unregister_class(MATHP_OT_refresh_preview)
