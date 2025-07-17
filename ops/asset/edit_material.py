import bpy

from ...debug import DEBUG_EDIT_MATERIAL
from ...utils.window import PreviewMaterialWindow


class EditMaterial(bpy.types.Operator):
    bl_idname = 'mathp.edit_material_asset'
    bl_label = 'Edit Material Asset'

    edit_material = None
    count = None
    # timer = None
    window: PreviewMaterialWindow = None

    @classmethod
    def poll(cls, context):
        return (hasattr(context, 'selected_assets') and context.selected_assets) or context.asset

    def invoke(self, context, event):
        if res := self.execute(context):
            if "FINISHED" not in res:
                self.exit(context)
                return res
        self.window = PreviewMaterialWindow(self, context, event, self.edit_material)
        if DEBUG_EDIT_MATERIAL:
            self.count = 0
        print(self.bl_idname, self.edit_material)
        self.timer = context.window_manager.event_timer_add(1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if self.window.check(self, context):
            return {"PASS_THROUGH"}

        self.exit(context)
        return {"FINISHED"}

    def execute(self, context):
        """执行弹出窗口"""
        if res := self.find_material(context):
            return res
        return {'FINISHED'}

    def exit(self, context):
        if DEBUG_EDIT_MATERIAL:
            print("exit")
        if self.timer:
            context.window_manager.event_timer_remove(self.timer)
        self.window.exit()
        self.edit_material = None

    def cancel(self, context):
        self.exit(context)
        print("cancel", self.edit_material)

    def find_material(self, context):
        from ...utils import get_local_selected_assets

        match_obj = get_local_selected_assets(context)
        selected_mat = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        if not selected_mat:
            self.report({'WARNING'}, '请选择一个本地材质资产')
            return {"CANCELLED"}

        self.edit_material = selected_mat[0]
