import bpy

from .align import Align
from .material import Material
from .sync import Sync
from .window import Window
from .. import __package__ as base_package
from ..utils.keymap import draw_kmi


class MaterialHelperPreference(bpy.types.AddonPreferences, Material, Window, Align, Sync):
    bl_idname = base_package

    show_text: bpy.props.BoolProperty(name="Show Text", default=False)

    def draw(self, context):
        layout = self.layout
        self.draw_settings(context, layout)

    def draw_settings(self, context, layout):
        col = layout.column()
        col.use_property_split = True

        box = col.box()
        box.label(text='Edit Material Asset', icon='MATERIAL')
        row = box.row(align=True)
        row.prop(self, 'show_text', expand=True)

        self.draw_window(box)
        self.draw_material(box)

        col.separator()
        self.draw_align(col)

def register():
    bpy.utils.register_class(MaterialHelperPreference)


def unregister():
    bpy.utils.unregister_class(MaterialHelperPreference)
