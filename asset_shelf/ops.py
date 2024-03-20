import bpy
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator
from pathlib import Path
import blf
import gpu
import math
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_texture_2d
from bpy.app.translations import pgettext_iface as _p

from .raycast import ray_cast


class AssetUser:
    @classmethod
    def poll(cls, context) -> bool:
        # return context.asset.metadata.catalog_id in catalog_id_poll
        return context.asset and context.asset.local_id

    def ensure_asset(self, context):
        asset_dis = context.asset
        self.blend_path = asset_dis.full_library_path
        self.asset_name = asset_dis.name
        self.asset_dir = Path(self.blend_path).parent
        self.material = context.asset.local_id
        bpy.ops.asset.library_refresh()

    def ensure_mat_image(self, context):
        asset = context.asset.local_id
        asset_preview = asset.preview
        img = bpy.data.images.new('mathp_preview', *asset_preview.image_size, alpha=True)
        img.file_format = "PNG"
        try:
            img.pixels.foreach_set(asset_preview.image_pixels_float)
        except TypeError:
            print(f"Could not save thumbnail from '{asset.name}'")
        return img


class MATHP_OT_asset_double_click(AssetUser, Operator):
    bl_idname = "mathp.mat_double_click"
    bl_label = "Edit"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Double click to %s"

    def execute(self, context):
        bpy.ops.asset.library_refresh()
        mat = context.asset.local_id
        bpy.ops.mathp.edit_material_asset("INVOKE_DEFAULT", material=mat.name)
        return {'FINISHED'}


class MATHP_OT_asset_delete(AssetUser, Operator):
    bl_idname = "mathp.asset_delete"
    bl_label = "Delete"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Delete %s"

    @classmethod
    def description(cls, context, event):
        return "Delete %s" % context.asset.local_id.name

    def execute(self, context):
        mat = context.asset.local_id
        bpy.data.materials.remove(mat)
        return {'FINISHED'}


class MATHP_OT_asset_rename(AssetUser, Operator):
    bl_idname = "mathp.asset_rename"
    bl_label = "Rename"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        active = context.asset.local_id

        layout = self.layout
        layout.label(text='Rename')
        layout.prop(active, 'name', text='', icon='MATERIAL')

    def execute(self, context):
        return context.window_manager.invoke_popup(self)


class MATHP_OT_asset_copy(AssetUser, Operator):
    bl_idname = "mathp.asset_copy"
    bl_label = "Copy"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mat = context.asset.local_id
        new_mat = mat.copy()
        new_mat.asset_mark()

        return {'FINISHED'}


def ui_scale():
    # return bpy.context.preferences.system.dpi * bpy.context.preferences.system.pixel_size / 72
    return bpy.context.preferences.system.dpi * 1 / 72


def draw_callback_px(self, context):
    # draw text
    font_id = 0

    offsetX = 20 * ui_scale()
    offsetY = 20 * ui_scale()
    sep_x = 5 * ui_scale()
    sep_y = 5 * ui_scale()

    font_size = 15 * ui_scale()
    img_size = 64 * ui_scale()
    img_start_pt = (self.mouse_x + offsetX, self.mouse_y - offsetY + img_size / 2 + font_size)
    title_start_pt = img_start_pt[0], img_start_pt[1] + img_size + sep_y * 2

    blf.color(font_id, 1, 1, 1, 0.5)
    blf.size(font_id, font_size)
    blf.position(font_id, self.mouse_x + offsetX, self.mouse_y, 0)
    if self.target_obj:
        blf.draw(font_id, self.asset_name + ' > ' + self.target_obj.name)
    else:
        blf.draw(font_id, self.asset_name)

    # draw image
    img = self.draw_img
    if self.draw_img:
        gpu.state.blend_set("ALPHA")  # enable alpha blend
        texture = gpu.texture.from_image(img)
        draw_texture_2d(texture, img_start_pt, img_size, img_size)
        gpu.state.blend_set("NONE")


class ADJT_OT_asset_drag_drop(AssetUser, Operator):
    bl_idname = "mathp.mat_drag_drop"
    bl_label = "Apply Asset"
    bl_description = "Select those bones that are used in this pose"
    bl_options = {'REGISTER', 'UNDO'}

    _handle = None
    target_obj = None
    draw_img = None

    def execute(self, context):
        if self.target_obj:
            self.assign_material()

        return {'FINISHED'}

    def is_drop_action(self):
        return True

    def assign_material(self):
        # if target has material slot
        if self.target_obj.material_slots:
            self.target_obj.material_slots[0].material = self.material
        else:
            # create new slot
            self.target_obj.data.materials.append(self.material)

    def invoke(self, context, event):
        self.ensure_asset(context)
        self.load_pv_image(context)

        self.target_obj = None
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y
        self.region = [region for region in context.area.regions if region.type == 'WINDOW'][0]

        # add handle
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        self.update_area(context)
        return {"RUNNING_MODAL"}

        # get the ray_cast object

    def modal(self, context, event):
        self.update_area(context)  # hack method for update drawing handle
        if event.type == 'MOUSEMOVE':
            delta_x = event.mouse_region_x - self.mouse_x
            delta_y = event.mouse_region_y - self.mouse_y

            if self.is_drop_action():
                result, target_obj, view_point, world_loc, normal, location, matrix = ray_cast(context, event)
                if result:
                    self.target_obj = target_obj
                else:
                    self.target_obj = None

            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if self.is_drop_action():
                if self.target_obj:
                    context.view_layer.objects.active = self.target_obj
                    self.execute(context)
                else:
                    self.report({'WARNING'}, 'No object under mouse')

            self.remove_handle(context)

            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.remove_handle(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def remove_handle(self, context):
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        self.remove_pv_image()

    def update_area(self, context):
        # update the area
        context.area.tag_redraw()

    def load_pv_image(self, context):
        self.draw_img = self.ensure_mat_image(context)

    def remove_pv_image(self):
        if self.draw_img:
            bpy.data.images.remove(self.draw_img)


def register():
    bpy.utils.register_class(MATHP_OT_asset_double_click)
    bpy.utils.register_class(ADJT_OT_asset_drag_drop)
    bpy.utils.register_class(MATHP_OT_asset_delete)
    bpy.utils.register_class(MATHP_OT_asset_rename)
    bpy.utils.register_class(MATHP_OT_asset_copy)


def unregister():
    bpy.utils.unregister_class(MATHP_OT_asset_double_click)
    bpy.utils.unregister_class(ADJT_OT_asset_drag_drop)
    bpy.utils.unregister_class(MATHP_OT_asset_delete)
    bpy.utils.unregister_class(MATHP_OT_asset_rename)
    bpy.utils.unregister_class(MATHP_OT_asset_copy)
