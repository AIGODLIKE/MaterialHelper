import blf
import bpy
import gpu.matrix
from bpy.app.translations import pgettext_iface
from mathutils import Vector

from .public_material import PublicMaterial
from ...utils import get_pref
from ...utils.gpu import (
    draw_2d_texture,
    from_material_get_gpu_texture_by_pixel,
    draw_rounded_rectangle_area,
)
from ...utils.mesh import from_face_index_get_material_index
from ...utils.translate import translate_lines_text


def offset_material_list(items, offset, count) -> list:
    il = len(items)
    if count > il:
        return items
    elif (offset + count) > il - 1:
        return items[offset:offset + count]
    else:
        return items[offset:offset + count]


class Draw:

    def draw_handler(self, context):
        active_material = context.scene.material_helper_property.active_material
        if active_material is None:
            return
        elif self.area_hash != hash(context.area):
            return
        material = active_material.material
        if (active_material is not None) and (material is not None):
            self.draw_material_bar(context)
            if not self.draw_info.get("in_bar", None):
                self.draw_texts(context)
                self.draw_material(material, offset=(20, 20))
            self.draw_bar_info(context)

    def draw_texts(self, context):
        with gpu.matrix.push_pop():
            active_material = context.scene.material_helper_property.active_material
            material = active_material.material
            x, y = self.offset + Vector((50, 0))
            blf.position(0, 0, 0, 1)
            gpu.matrix.translate((x, y))
            text = bpy.app.translations.pgettext_iface("Assign material")
            blf.size(0, 15)
            texts = [
                text + ": " + self.pick_hub_text(material.name),
            ]
            in_bar = self.draw_info.get("in_bar", None)
            in_move_bar_by_drag = self.draw_info.get("in_move_bar_by_drag", None)
            is_dragging_outside_bar = self.draw_info.get("is_dragging_outside_bar", None)
            # blf.draw(0, f"{self.bar_offset} {in_bar} {in_move_bar_by_drag} {is_dragging_outside_bar}")

            self.draw_text_list(texts)

    def pick_hub_text(self, name) -> str:
        text = name
        (result, material_obj, material, index) = self.pick_info
        if result:
            if material is not None:
                text += f" -> {material_obj.name}"

            if material_obj and material_obj.type == "MESH":
                material_index = from_face_index_get_material_index(material_obj, index)
                slot_name = pgettext_iface("Material slot")
                text += f"({slot_name} {material_index})"
        return text

    def draw_material_bar(self, context):
        """
            {'FOOTER',
            'ASSET_SHELF_HEADER',
             'NAVIGATION_BAR',
              'UI',
               'TOOL_HEADER',
                'ASSET_SHELF',
                 'HEADER',
                  'CHANNELS', 'HUD', 'TOOLS', 'EXECUTE', 'WINDOW'}
                  """
        gpu.state.blend_set("ALPHA")

        pref = get_pref()
        bar_scale = pref.picker_material_preview_bar_scale
        bottom_offset = pref.picker_material_bottom_offset

        area = context.area
        width = area.width
        ui_width = 0
        tools_width = 0
        asset_shelf_height = 0
        for region in area.regions:
            if region.type == "UI":
                ui_width = region.width
            elif region.type == "TOOLS":
                tools_width = region.width
            elif region.type == "ASSET_SHELF":
                asset_shelf_height = region.height
        wa, wb = tools_width, width - ui_width

        item_size = 32 * bar_scale  # 单个图标宽
        ha = asset_shelf_height + bottom_offset
        hb = ha + item_size

        draw_width = wb - wa
        draw_height = hb - ha
        point = (wa, ha), (wb, hb)

        draw_item_count = int(draw_width // item_size)
        item_width = draw_width / draw_item_count

        self.draw_info["draw_point"] = point
        self.draw_info["draw_xy"] = (wa, wb), (ha, hb)
        self.draw_info["draw_start_x"] = wa
        self.draw_info["draw_item_count"] = draw_item_count
        self.draw_info["draw_item_size"] = (item_width, item_size)

        with gpu.matrix.push_pop():
            background_color = pref.picker_material_preview_bar_background_color
            gpu.matrix.translate((wa, bottom_offset))
            gpu.matrix.translate((draw_width / 2, draw_height / 2))
            draw_rounded_rectangle_area(width=draw_width, height=draw_height, color=background_color)
        with gpu.matrix.push_pop():
            gpu.matrix.translate((wa, bottom_offset))
            active_material = context.scene.material_helper_property.active_material
            for material in offset_material_list(self.start_material_list, self.bar_offset, draw_item_count):
                gpu.state.blend_set("ALPHA")
                if material in self.texture_cache:
                    texture = self.texture_cache[material]
                else:
                    texture = from_material_get_gpu_texture_by_pixel(material)
                    if texture is None:
                        return
                    self.texture_cache[material] = texture
                if active_material and active_material.material and material == active_material.material:
                    with gpu.matrix.push_pop():
                        gpu.matrix.translate((item_width / 2, item_size / 2))
                        draw_rounded_rectangle_area(width=item_width, height=item_size,
                                                    color=list(i + .1 for i in background_color))

                icon_w, icon_h = material.preview.icon_size[:]
                draw_2d_texture(texture, icon_w, icon_h, bar_scale)
                gpu.matrix.translate((item_width, 0))

    def draw_bar_info(self, context):
        bar_material = self.draw_info.get("bar_material", None)
        bar_index = self.draw_info.get("bar_index", None)
        in_bar = self.draw_info.get("in_bar", None)
        is_drag_material = self.draw_info.get("is_drag_material", None)
        if bar_material and in_bar:
            with gpu.matrix.push_pop():
                blf.position(0, 0, 0, 1)
                # blf.draw(0, str(bar_material) + f"  {bar_index}")
                gpu.matrix.translate(self.offset)
                blf.draw(0, bar_material.name)


class MaterialAssignByModal(PublicMaterial, Draw, bpy.types.Operator):
    bl_idname = "mathp.material_assign_by_modal"
    bl_label = "Assign material by modal"
    bl_options = {"REGISTER", "UNDO"}

    header_text = "Material Assign by modal"
    default_cursor = "CROSS"
    draw_paint_bucket = False
    area_hash = None
    draw_info = {}
    bar_offset = 0
    start_material_list = None

    @classmethod
    def description(cls, context, properties):
        material = getattr(context, "material", None)
        texts = [
            "Ctrl:Continuous assign material",
            "Shift:Assign the materials of all selected objects",
        ]
        if context.mode == "EDIT_MESH":
            texts.extend((
                "",
                "Alt:Assign a selection face",
            ))
        material_name = material.name if material is not None else ""
        material_name += "\n\n"
        return material_name + translate_lines_text(*texts)

    @classmethod
    def poll(cls, context):
        return context.region and context.region.type == "WINDOW"

    def start(self, context, event):
        self.area_hash = hash(context.area)
        self.draw_info = {}
        self.bar_offset = 0

        picker_material_list = context.scene.material_helper_property.picker_material_list
        material_list = [mi.material for mi in picker_material_list if mi and mi.material and mi.material.preview][:]
        self.start_material_list = material_list

    def click(self, context, event):
        active_material = context.scene.material_helper_property.active_material
        (result, material_obj, material, index) = self.pick_info
        if result and material_obj and active_material:
            active_material.assign_material(context, material_obj, index, event.alt)

    def modal(self, context, event):
        self.offset = Vector((event.mouse_region_x, event.mouse_region_y))

        self.draw_info["in_bar"] = in_bar = self.check_mouse_in_bar_area(event)
        start_bar_index = self.draw_info.get("start_bar_index", None)
        bar_index = self.draw_info.get("bar_index")
        print(event.value, event.type, in_bar, start_bar_index, bar_index)
        if res := self.left_mouse_scroll_bar(context, event):
            return res
        elif res := self.mouse_up_down_wheel_scroll_bar(context, event):
            return res
        return super().modal(context, event)

    def check_mouse_in_bar_area(self, event):

        """输入一个event和xy的最大最小值,反回一个鼠标是否在此区域内的布尔值,如果在里面就反回True

        Args:
            event (bpy.types.Event): 输入操作符event
            area_point ((x,x),(y,y)): 输入x和y的坐标
        """
        if "draw_xy" not in self.draw_info:
            return False
        x, y = self.draw_info["draw_xy"]
        mou_x, mou_y = event.mouse_region_x, event.mouse_region_y
        x_in = min(x) < mou_x < max(x)
        y_in = min(y) < mou_y < max(y)
        return x_in and y_in

    def get_now_mouse_bar_index(self, event) -> int:
        if "draw_start_x" not in self.draw_info:
            return -1
        start_x = self.draw_info["draw_start_x"]
        iw, _ = self.draw_info["draw_item_size"]
        x = event.mouse_region_x - start_x
        return int(x // iw)

    def left_mouse_scroll_bar(self, context, event):
        """左键鼠标滚动材质栏"""

        in_bar = self.draw_info["in_bar"]

        bar_index = self.get_now_mouse_bar_index(event)
        bar_offset_index = bar_index + self.bar_offset
        self.draw_info["bar_index"] = bar_offset_index
        try:
            bar_material = self.draw_info["bar_material"] = self.start_material_list[bar_offset_index]
        except IndexError:
            bar_material = self.draw_info["bar_material"] = None
            ...

        if not in_bar:
            self.draw_info["is_dragging_outside_bar"] = True

        if "mouse_press_in_bar" in self.draw_info and event.type == "MOUSEMOVE":
            start_move = bar_index != self.draw_info["start_bar_index"] and in_bar
            if (start_move or ("in_move_bar_by_drag" in self.draw_info)) and "is_drag_material" not in self.draw_info:
                self.bar_offset = self.draw_info["start_bar_offset"] - (bar_index - self.draw_info["start_bar_index"])
                if "in_move_bar_by_drag" not in self.draw_info:
                    self.draw_info["in_move_bar_by_drag"] = True
                self.limitation_offset_index()
            elif not in_bar:
                if "is_drag_material" not in self.draw_info:
                    self.draw_info["is_drag_material"] = True
                    context.scene.material_helper_property.try_picker_material(bar_material)

            context.area.tag_redraw()
            return {"RUNNING_MODAL"}

        if event.type == "LEFTMOUSE":
            if event.value == "PRESS" and in_bar:
                self.draw_info["mouse_press_in_bar"] = in_bar
                self.draw_info["start_bar_index"] = bar_index
                self.draw_info["start_bar_offset_index"] = bar_offset_index
                self.draw_info["start_bar_offset"] = self.bar_offset
                return {"RUNNING_MODAL"}
            elif event.value == "RELEASE" and "mouse_press_in_bar" in self.draw_info:
                self.draw_info.pop("mouse_press_in_bar")

                if (
                        self.draw_info["start_bar_index"] == bar_index and
                        "in_move_bar_by_drag" not in self.draw_info and
                        in_bar
                ):
                    material_list = self.start_material_list
                    material_index = self.bar_offset + bar_index
                    if len(material_list) - 1 >= material_index:
                        material = material_list[material_index]
                        context.scene.material_helper_property.try_picker_material(material)
                        self.draw_info.clear()
                        self.draw_info["in_bar"] = in_bar
                        self.draw_info["bar_material"] = material
                        self.draw_info["bar_index"] = bar_index
                        return {"RUNNING_MODAL"}
                self.draw_info.clear()
                self.draw_info["in_bar"] = in_bar
                self.draw_info["bar_material"] = bar_material
                self.draw_info["bar_index"] = bar_index

    def mouse_up_down_wheel_scroll_bar(self, context, event):
        """鼠标中键滚动材质栏"""
        if self.draw_info.get("in_bar", None):
            if event.type in {"WHEELDOWNMOUSE", "WHEELUPMOUSE"}:
                if event.type == "WHEELDOWNMOUSE":
                    self.bar_offset += 1
                elif event.type == "WHEELUPMOUSE":
                    self.bar_offset -= 1
                self.limitation_offset_index()
                context.area.tag_redraw()
                return {"RUNNING_MODAL"}

    def limitation_offset_index(self):
        ml = len(self.start_material_list)
        draw_item_count = self.draw_info["draw_item_count"]
        max_bar_offset = int(ml - draw_item_count) + 1
        self.bar_offset = min(max_bar_offset, max(0, self.bar_offset))
