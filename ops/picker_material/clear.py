import bpy



class MaterialClear(bpy.types.Operator):
    bl_idname = "mathp.material_clear"
    bl_label = "Clear"
    bl_description = "Clear material board"

    @classmethod
    def poll(cls, context):
        return len(context.scene.material_helper_property.picker_material_list) != 0

    def execute(self, context):
        context.scene.material_helper_property.picker_material_list.clear()
        return {"FINISHED"}
