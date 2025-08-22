import blf
import bpy
import gpu.matrix
from bpy.app.translations import pgettext_iface
from mathutils import Vector

from .public_material import PublicMaterial
from ...debug import DEBUG_PICKER_MATERIAL
from ...utils.translate import translate_lines_text


class MaterialPicker(bpy.types.Operator, PublicMaterial):
    bl_idname = "mathp.material_picker"
    bl_label = "Picker Material"
    bl_options = {"REGISTER"}

    header_text = "Ctrl:Continuous pick    Alt:Pick object all material"

    @classmethod
    def description(cls, context, properties):
        return translate_lines_text(
            "\n",
            "Ctrl: Pick all material in asset",
            "Shift: Picker the materials of all selected objects",
            "Alt: Pick all materials in the scene",
        )

    @property
    def pick_hub_text(self) -> str:
        text = "None"
        (result, material_obj, material, index) = self.pick_info
        if result:
            text = f"{material_obj.name}"
            if material is not None:
                text += f" -> {material.name}"
        return text

    def draw_handler_texts(self, context):
        (start_result, start_material_obj, start_material, start_index) = self.start_pick_info
        x, y = self.offset + Vector((50, 0))
        with gpu.matrix.push_pop():
            blf.position(0, 0, 0, 1)
            gpu.matrix.translate((x, y))

            texts = [
                pgettext_iface("Picker Material"),
            ]

            objects_name = list((i.name for i in context.selected_objects))
            select_count = len(objects_name)
            event = self.event

            if start_result:
                face_index = pgettext_iface("Face Index")
                assign = pgettext_iface("Assign material")
                text = f"{assign}: {start_material_obj.name} -> {face_index}:{start_index}"
                texts.append(text)

            if select_count:
                text = pgettext_iface("Assign material to %i objects %s")
                names = objects_name
                if select_count > 5:
                    names = [*names[:5], "..."]
                texts.append(text % (select_count, ",".join(names)))

            if event.alt:
                texts.append(pgettext_iface("Picker the materials of all selected objects"))
            if event.ctrl:
                texts.append(pgettext_iface("Continuous picker material"))
            texts.append(self.pick_hub_text)
            self.draw_text_list(texts)

    def draw_handler(self, context):
        if hash(context.area) == self.start_area_hash:
            (result, material_obj, material, index) = self.pick_info
            self.draw_handler_texts(context)
            if result and material is not None:
                self.draw_material(material)

    def start(self, context, event):
        if DEBUG_PICKER_MATERIAL:
            print("start", event.value, event.type, event.alt, event.shift, event.ctrl)

        material_helper_property = context.scene.material_helper_property
        self.update(context, event)

        if event.type == "BUTTON4MOUSE":  # 拾取材质到所有选中的物体
            (start_result, start_material_obj, start_material, start_index) = self.start_pick_info
            if start_result:
                text = pgettext_iface("Assign picker material to %s -> %i")
                self.header_text = text % (start_material_obj.name, start_index)
            else:
                text = pgettext_iface("Assign picker material to %i objects %s")
                objects_name = list((i.name for i in context.selected_objects))
                self.header_text = text % (len(objects_name), ",".join(objects_name))
        else:
            if event.shift:  # 拾取所有选择物体材质
                count = 0
                for obj in context.selected_objects:
                    if obj.type == "MESH":
                        for material in obj.data.materials:
                            if material_helper_property.try_picker_material(material):
                                count += 1
                text = pgettext_iface("%i materials have been picker") % count
                self.report({"INFO"}, text)
                return True
            elif event.ctrl:  # 拾取所有资产
                for mat in bpy.data.materials:
                    if mat.asset_data:
                        material_helper_property.try_picker_material(mat)
                return True
            elif event.alt:  # 拾取所有场景材质
                count = 0
                for obj in context.scene.objects:
                    if obj.type == "MESH":
                        for material in obj.data.materials:
                            if material_helper_property.try_picker_material(material):
                                count += 1

                text = pgettext_iface("%i materials have been picker") % count
                self.report({"INFO"}, text)
                return True
        return False

    def click(self, context, event):
        """拾取材质
        在按下左键时"""
        self.picker_material(context, event)
        self.asset_material(context, event)

    def picker_material(self, context, event):
        result, material_obj, material, index = self.pick_info
        if DEBUG_PICKER_MATERIAL:
            print("picker_material")

        material_helper_property = context.scene.material_helper_property
        if event.alt:  # 拾取所有物体的材质
            picker_count = 0
            for material in material_obj.data.materials:
                if material is not None:
                    if material_helper_property.try_picker_material(material):
                        picker_count += 1
            self.report({"INFO"}, pgettext_iface("Picker material: %i") % picker_count)
        elif material_obj:
            if material is not None:
                material_helper_property.try_picker_material(material)

    def asset_material(self, context, event):

        result, material_obj, material, index = self.pick_info
        material_helper_property = context.scene.material_helper_property
        active_material = material_helper_property.active_material

        if DEBUG_PICKER_MATERIAL:
            print("asset_material", result, material_obj, material, index, event.alt, active_material)

        if result and active_material:
            start_result, start_material_obj, _, start_index = self.start_pick_info
            if start_result and start_material_obj:
                active_material.assign_material(context, start_material_obj, start_index, assign_obj=False)

            objects_name = []
            for obj in context.selected_objects:
                objects_name.append(obj.name)
                if context.mode == "EDIT_MESH" and obj.mode == "EDIT" and obj.type == "MESH":
                    from .assign_by_item import MaterialAssignByItem
                    if MaterialAssignByItem.assign_to_select_face(context, obj, active_material.material):
                        continue
                active_material.assign_material(context, obj, 0, assign_obj=True)

        else:
            self.report({"INFO"}, pgettext_iface("Material not picked up"))
