import bpy
from ..prefs.get_pref import get_pref


class MATHP_PT_NodePanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Preview"
    bl_idname = "MATHP_PT_NodePanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Node'

    @classmethod
    def poll(cls, context):
        return get_pref().window_style == '2'

    def draw(self, context):
        layout = self.layout
        layout.template_ID_preview(context.object, 'active_material',
                                   hide_buttons=True,
                                   rows=5, cols=5)


def register():
    bpy.utils.register_class(MATHP_PT_NodePanel)


def unregister():
    bpy.utils.unregister_class(MATHP_PT_NodePanel)
