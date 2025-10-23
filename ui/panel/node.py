import bpy


class MATHP_PT_Node_edit_Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Preview"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Node"

    @classmethod
    def poll(cls, context):
        windows = context.window_manager.windows
        return len(windows) > 1 and context.window == windows[-1]

    def draw(self, context):
        layout = self.layout
        if context.object and context.object.active_material:
            layout.template_ID_preview(context.object, "active_material",
                                       hide_buttons=True,
                                       rows=5, cols=5)
            row = layout.row(align=True)
            row.prop(context.object.active_material, "preview_render_type", expand=True)


class MATERIAL_PT_Node_tool_Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Material Helper"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        from ...ops.align_nodes import MATHP_OT_move_dependence, MATHP_OT_align_dependence
        layout = self.layout.column()
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator(MATHP_OT_move_dependence.bl_idname)
        layout.operator(MATHP_OT_align_dependence.bl_idname)
