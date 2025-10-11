import bpy


class MATHP_OT_select_material_obj(bpy.types.Operator):
    bl_idname = "mathp.select_material_obj"
    bl_label = "Select Material Object"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_assets') and context.selected_assets and context.mode == "OBJECT"

    def execute(self, context):
        from ..utils import get_local_selected_assets
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]
        for obj in context.scene.objects:
            if materials := getattr(obj.data, "materials", None):
                for mat in materials:
                    if mat in selected_mats:
                        obj.select_set(True)
        return {"FINISHED"}
