import bpy

from ..utils.property import import_material


class MATHP_OT_add_material(bpy.types.Operator):
    """Add Material"""
    bl_idname = "mathp.add_material"
    bl_label = "Add Material"
    bl_options = {"REGISTER", "UNDO"}

    file_path: bpy.props.StringProperty(subtype="FILE_PATH")
    dep_class = []  # 动态ops

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_assets")

    def execute(self, context):
        self.material = material = import_material(self.file_path)
        material.asset_mark()
        bpy.ops.asset.library_refresh()
        material.asset_generate_preview()
        context.area.spaces[0].activate_asset_by_id(material)
        context.area.tag_redraw()
        bpy.ops.asset.library_refresh()
        return {"FINISHED"}

    # def invoke(self, context, event):
    #     self.count = 0
    #     self.execute(context)
    #     self.timer = context.window_manager.event_timer_add(0.01, window=context.window)
    #     context.window_manager.modal_handler_add(self)
    #     return {"RUNNING_MODAL"}
    #
    # def modal(self, context, event):
    #     if event.type == "TIMER":
    #         if self.count < 10:
    #             self.count += 1
    #         else:
    #             context.area.spaces[0].activate_asset_by_id(self.material)
    #             context.area.tag_redraw()
    #
    #             if self.timer:
    #                 context.window_manager.event_timer_remove(self.timer)
    #                 self.timer = None
    #                 return {"FINISHED"}
    #
    #     return {"PASS_THROUGH"}
