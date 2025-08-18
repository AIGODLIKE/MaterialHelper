import blf
import bpy
import gpu.matrix
from mathutils import Vector

from ...src import paint_bucket_load_texture
from ...utils import get_pref
from ...utils.area import find_mouse_in_area
from ...utils.gpu import draw_2d_texture, from_material_get_gpu_texture_by_pixel
from ...utils.mesh import from_face_index_get_material
from ...utils.ray_cast import mouse_2d_ray_cast


def from_mouse_get_material(context, event):
    """
    2d to 3d
    xrcy
    """
    mouse = Vector((event.mouse_region_x, event.mouse_region_y))
    result, location, normal, index, ray_obj, matrix = mouse_2d_ray_cast(context, mouse)
    # result, location, normal, index, ray_obj, matrix = mouse_2d_ray_cast_by_mouse_area(context, event)
    if result:
        material = from_face_index_get_material(ray_obj, index)
        return True, ray_obj, material, index
    return False, None, None, None


class PublicMaterial:
    continuous: bpy.props.BoolProperty()
    view_3d_handler = None

    start_area_hash = None
    offset = None
    pick_info = None  # (result, material_obj, material, index)
    start_pick_info = None
    cursor = None
    header_text = None
    default_cursor = "EYEDROPPER"
    texture_cache = {}
    event = None

    def invoke(self, context, event):
        self.event = event
        self.continuous = event.ctrl
        self.offset = Vector((event.mouse_region_x, event.mouse_region_y))
        self.start_pick_info = self.pick_info = from_mouse_get_material(context, event)
        self.texture_cache = {}
        if context.area.type == "VIEW_3D":
            if self.start(context, event):
                return {"FINISHED"}
            context.window_manager.modal_handler_add(self)
            context.window.cursor_set(self.default_cursor)
            if self.__class__.view_3d_handler is None:
                self.start_area_hash = hash(context.area)
                if self.header_text and context.area:
                    header_text = bpy.app.translations.pgettext_iface(self.header_text)
                    context.area.header_text_set(header_text)
                self.__class__.view_3d_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_handler,
                                                                                        (context,),
                                                                                        "WINDOW",
                                                                                        "POST_PIXEL")
                bpy.ops.ed.undo_push(message="Push Undo")
                return {"RUNNING_MODAL"}
        self.report({"INFO"}, "Not find 3d view")
        return {"CANCELLED"}

    def update(self, context, event):
        if context.area:
            context.area.tag_redraw()

    def update_cursor(self, context, event):
        area = find_mouse_in_area(context, event)
        is_picker = area and area.type == "VIEW_3D" and hash(area) == self.start_area_hash
        cursor = self.default_cursor if is_picker else "STOP"
        if self.cursor != cursor:
            context.window.cursor_set(cursor)
            self.cursor = cursor

    def modal(self, context, event):
        """
        TODO: 多个窗口拾取
        """
        try:
            self.event = event
            self.offset = Vector((event.mouse_region_x, event.mouse_region_y))
            self.update_cursor(context, event)
            self.pick_info = from_mouse_get_material(context, event)
            self.update(context, event)
            is_left = event.type == "LEFTMOUSE"
            is_right = event.type == "RIGHTMOUSE"
            is_release = event.value == "RELEASE"
            is_press = event.value == "PRESS"
            is_space = event.type == "SPACE"

            if is_left and is_release:
                if self.click(context, event):
                    self.exit(context)
                    return {"FINISHED"}
                if not self.continuous and not event.ctrl:
                    self.exit(context)
                    return {"FINISHED"}
            elif (is_right or is_space) and is_press:
                self.exit(context)
                return {"CANCELLED"}
            elif event.type in ("INBETWEEN_MOUSEMOVE", "WHEELDOWNMOUSE", "WHEELUPMOUSE", "MIDDLEMOUSE"):
                return {"PASS_THROUGH"}
            return {"RUNNING_MODAL"}
        except Exception as e:
            import traceback
            print(self.pick_info)
            print(e)
            traceback.print_exc()
            traceback.print_stack()
            self.exit(context)
            return {"CANCELLED"}

    def remove_view_3d_handler(self):
        if self.__class__.view_3d_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.__class__.view_3d_handler, "WINDOW")
            self.__class__.view_3d_handler = None

    def exit(self, context):
        self.remove_view_3d_handler()
        context.window.cursor_set("DEFAULT")
        context.area.header_text_set(None)
        self.start_area_hash = None
        self.event = None

    def draw_material(self, material, offset=(50, 30)):
        pref = get_pref()
        with gpu.matrix.push_pop():
            gpu.state.blend_set("ALPHA")
            gpu.state.depth_test_set("NONE")
            gpu.matrix.translate(self.offset)

            if getattr(self, "draw_paint_bucket", False):
                draw_2d_texture(paint_bucket_load_texture(), 30, 30)
            if material in self.texture_cache:
                texture = self.texture_cache[material]
            else:
                texture = from_material_get_gpu_texture_by_pixel(material)
                if texture is None:
                    return
                self.texture_cache[material] = texture
            w, h = material.preview.icon_size[:]
            gpu.matrix.translate(offset)
            draw_2d_texture(texture, w, h, pref.picker_material_preview_scale)

    def draw_text_list(self, data):
        with gpu.matrix.push_pop():
            blf.position(0, 0, 0, 1)
            blf.size(0, 15)
            for text in data:
                if isinstance(text, dict):
                    size = text["size"]
                    color = text["color"]
                    text = text["text"]
                    if len(color) == 3:
                        color.append(1)
                    blf.color(0, *color)
                    blf.size(0, size)
                gpu.matrix.translate((0, -20))
                blf.draw(0, text)
