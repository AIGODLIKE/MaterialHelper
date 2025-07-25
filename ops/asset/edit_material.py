import bpy

from ...utils.refresh_material import async_refresh_material, dprint
from ...utils.window import PreviewMaterialWindow


class EditMaterial(bpy.types.Operator):
    bl_idname = "mathp.edit_material_asset"
    bl_label = "Edit Material Asset"

    edit_material = None
    count = 0
    timer = None
    window: "PreviewMaterialWindow|None" = None

    @classmethod
    def poll(cls, context):
        return (hasattr(context, "selected_assets") and context.selected_assets) or context.asset

    def invoke(self, context, event):
        if res := self.execute(context):
            if "FINISHED" not in res:
                self.exit(context)
                return res
        if len(context.window_manager.windows) > 10:
            return {"FINISHED"}
        self.window = PreviewMaterialWindow(self, context, event, self.edit_material)
        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(1, window=context.window)

        dprint(self.bl_idname, self.edit_material)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        self.window.try_show_all_node(self, context)
        dprint(self.bl_idname, event.ctrl, event.type, event.value, self.count, end="\r")
        if event.type in ("Q", "O") and event.value == "PRESS":
            self.report({"WARNING"}, "Please close the preview window before proceeding with the operation")

            self.exit(context)
            bpy.ops.wm.window_close()
            return {"FINISHED"}
        elif self.window.check(self, context):
            return {"PASS_THROUGH"}
        self.exit(context)
        return {"FINISHED"}

    def execute(self, context):
        """执行弹出窗口"""
        if res := self.find_material(context):
            return res
        return {"FINISHED"}

    def exit(self, context):
        dprint("exit", self.bl_idname, context.area.type)
        if self.timer:
            context.window_manager.event_timer_remove(self.timer)
            dprint("self.timer", self.timer)
        if self.window:
            dprint("self.window", self.window)
            self.window.exit()
            self.window = None
        if self.edit_material:
            async_refresh_material(self.edit_material.name)
            self.edit_material = None

    def cancel(self, context):
        """关闭当前窗口时将会触发"""
        dprint("cancel", self.edit_material)
        self.exit(context)

    def find_material(self, context):
        from ...utils import get_local_selected_assets

        match_obj = get_local_selected_assets(context)
        selected_mat = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        if not selected_mat:
            self.report({"WARNING"}, "Please select a local material asset")
            return {"CANCELLED"}
        self.edit_material = selected_mat[0]
        return None
