import bpy

from .align import Align
from .material import Material
from .sync import Sync
from .window import Window
from .. import __package__ as base_package
from ..utils.keymap import draw_kmi


class MaterialHelperPreference(bpy.types.AddonPreferences, Material, Window, Align, Sync):
    bl_idname = base_package

    ui_page: bpy.props.EnumProperty(name='UI', items=[
        ('SETTINGS', 'Settings', '', 'PREFERENCES', 0),
        ('KEYMAP', 'Keymap', '', 'KEYINGSET', 1),
    ], default='SETTINGS')
    show_text: bpy.props.BoolProperty(name="Show Text", default=False)
    tips: bpy.props.StringProperty(update=lambda self, context: bpy.ops.mathp.tips(tips=self.tips))

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, 'ui_page', expand=True)

        getattr(self, f"draw_{self.ui_page.lower()}")(context, layout)

    def draw_settings(self, context, layout):
        col = layout.column()
        col.use_property_split = True

        box = col.box()
        box.label(text='Edit Material Asset', icon='MATERIAL')
        row = box.row(align=True)
        row.prop(self, 'show_text', expand=True)

        self.draw_window(box)

        col.separator()
        self.draw_align(col)

    def draw_keymap(self, context, layout):
        col = layout.box().column()
        col.label(text="Keymap", icon="KEYINGSET")
        km = None
        wm = context.window_manager
        kc = wm.keyconfigs.user

        old_km_name = ""
        get_kmi_l = []

        from ..keymaps import addon_keymaps

        for km_add, kmi_add in addon_keymaps:
            for km_con in kc.keymaps:
                if km_add.name == km_con.name:
                    km = km_con
                    break

            for kmi_con in km.keymap_items:
                if kmi_add.idname == kmi_con.idname and kmi_add.name == kmi_con.name:
                    get_kmi_l.append((km, kmi_con))

        get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

        for km, kmi in get_kmi_l:
            sub_col = col.column()
            if not km.name == old_km_name:
                sub_col.label(text=str(km.name), icon="DOT")

            if (not kmi.is_user_defined) and kmi.is_user_modified:
                sub_col.context_pointer_set("keymap", km)

            draw_kmi(sub_col, km, kmi)

            old_km_name = km.name


def register():
    bpy.utils.register_class(MaterialHelperPreference)


def unregister():
    bpy.utils.unregister_class(MaterialHelperPreference)
