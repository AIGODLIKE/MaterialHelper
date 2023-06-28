import bpy
from pathlib import Path
from .op_tmp_asset import selectedAsset
from .op_edit_material_asset import get_local_selected_assets, tag_redraw


class MATHP_OT_set_category(selectedAsset, bpy.types.Operator):
    bl_idname = 'mathp.set_category'
    bl_label = 'Set Category'

    @classmethod
    def poll(cls, context):
        if bpy.data.filepath != '':
            return super().poll(cls, context)

    def execute(self, context):
        folder = Path(bpy.data.filepath).parent
        target_catalog = "Catalog"

        objs = get_local_selected_assets(context)

        with (folder / "blender_assets.cats.txt").open() as f:
            for line in f.readlines():
                if line.startswith(("#", "VERSION", "\n")):
                    continue
                name = line.split(":")[2].split("\n")[0]
                if name == target_catalog:
                    uuid = line.split(":")[0]

                    for obj in objs:
                        asset = obj.asset_data
                        asset.catalog_id = uuid

        return {'FINISHED'}


def register():
    pass


def unregister():
    pass
