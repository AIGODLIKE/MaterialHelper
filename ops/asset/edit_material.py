from threading import Thread

import bpy

from ...debug import DEBUG_EDIT_MATERIAL
from ...utils.window import PreviewMaterialWindow


def refresh_material_asset_preview(name):
    """子进程刷新材质
    TIPS: 在关闭窗口时刷新会导致崩溃
    """
    material = bpy.data.materials[name]
    material.asset_generate_preview()
    with bpy.context.temp_override(id=material):
        bpy.ops.ed.lib_id_generate_preview()


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
        if DEBUG_EDIT_MATERIAL:
            print(self.bl_idname, self.edit_material)
        self.timer = context.window_manager.event_timer_add(2, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        self.window.try_show_all_node(self, context)
        if DEBUG_EDIT_MATERIAL:
            print(self.bl_idname, event.ctrl, event.type, event.value)
        if event.type in ("Q", "O") and event.value == "PRESS":
            self.report({"WARNING"}, "Please close the preview window before proceeding with the operation")
            self.exit(context)
            bpy.ops.wm.window_close()
            return {"CANCELLED"}
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
        if DEBUG_EDIT_MATERIAL:
            print("exit", self.bl_idname, context.area.type)
        if self.timer:
            context.window_manager.event_timer_remove(self.timer)
        if self.window:
            self.window.exit()
            self.window = None
        if self.edit_material:
            t = Thread(target=refresh_material_asset_preview, args=(self.edit_material.name,))
            t.start()
            t.join()
            self.edit_material = None

    def cancel(self, context):
        """关闭当前窗口时将会触发"""
        if DEBUG_EDIT_MATERIAL:
            print("cancel", self.edit_material)
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
