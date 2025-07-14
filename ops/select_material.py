import bpy


class MATHP_OT_select_material_obj(bpy.types.Operator):
    bl_idname = "mathp.select_material_obj"
    bl_label = "Select Material Object"
    bl_options = {"UNDO"}

    def execute(self, context):
        from ..utils import get_local_selected_assets
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]
        tmp_mesh = bpy.data.meshes.new("Temp")
        tmp_obj = bpy.data.objects.new("Temp", tmp_mesh)
        context.collection.objects.link(tmp_obj)
        bpy.context.view_layer.objects.active = tmp_obj

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        temp_obj = context.object
        for i, mat in enumerate(selected_mats):
            bpy.ops.object.material_slot_add()
            tmp_obj.material_slots[i].material = mat
        bpy.ops.object.select_linked(type="MATERIAL")
        bpy.data.objects.remove(temp_obj)
        return {"FINISHED"}
