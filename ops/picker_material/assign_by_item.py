import blf
import bmesh
import bpy
import gpu
from bpy.app.translations import pgettext_iface
from mathutils import Vector

from .public_material import PublicMaterial
from ...utils.mesh import from_face_index_get_material_index
from ...utils.translate import translate_lines_text


class MaterialAssignByItem(PublicMaterial, bpy.types.Operator):
    bl_idname = "mathp.material_assign_by_item"
    bl_label = "Assign material"
    bl_options = {"REGISTER", "UNDO"}

    header_text = "Ctrl:Continuous assign material    Alt:Assign object material"
    default_cursor = "DOT"
    draw_paint_bucket = True

    @classmethod
    def description(cls, context, properties):
        material = getattr(context, "material", None)
        texts = [
            "Shift:Assign the materials of all selected objects",
        ]
        if context.mode == "EDIT_MESH":
            texts.extend((
                "",
                "Alt:Assign a selection face",
            ))
        material_name = material.name if material is not None else ""
        material_name += "\n\n"
        objects_name = "\n".join([obj.name for obj in context.selected_objects])
        return material_name + translate_lines_text(*texts) + "\n\n" + objects_name

    def invoke(self, context, event):
        if event.alt and context.mode == "EDIT_MESH":  # 赋予到所选面
            material = getattr(context, "material", None)
            self.assign_to_select_face(context, context.object, material)
            return {"FINISHED"}
        elif event.shift:
            self.start(context, event)
            count = 0
            for obj in context.selected_objects:
                if obj.type == "MESH":
                    context.scene.material_helper_property.active_material.assign_material(context, obj, -1, True)
                    count += 1
            text = bpy.app.translations.pgettext_iface("Material assigned to %i objects") % count
            self.report({"INFO"}, text)
            return {"FINISHED"}
        return super().invoke(context, event)

    @staticmethod
    def assign_to_select_face(context, obj, material):
        """赋予到选择面"""
        with context.temp_override(context=obj, active_object=obj):
            material_slot = None
            if len(obj.material_slots) == 0:
                bpy.ops.object.material_slot_add()
                obj.material_slots[0].material = bpy.data.materials.new("Material Fill")

            for ms in obj.material_slots:  # 查找有没有材质相同的槽
                if ms.material == material:
                    material_slot = ms

            if material_slot is None:  # 如果没有相同材质的槽 就创建新的槽
                bpy.ops.object.material_slot_add()
                material_slot = obj.material_slots[-1]
                material_slot.material = material

            slot_index = material_slot.slot_index

            data = obj.data
            bm = bmesh.from_edit_mesh(data)
            for face in bm.faces:
                if face.select:
                    face.material_index = slot_index
            bmesh.update_edit_mesh(data)
            bm.free()

    def start(self, context, event):
        material = getattr(context, "material", None)
        picker_material = getattr(context, "picker_material", None)
        if picker_material is not None and material is not None:
            material_helper_property = context.scene.material_helper_property
            material_list = [m for m in context.scene.material_helper_property.picker_material_list]
            index = material_list.index(picker_material)
            material_helper_property.picker_material_list.move(index, 0)

    def click(self, context, event):
        (result, material_obj, material, index) = self.pick_info
        active_material = context.scene.material_helper_property.active_material
        if result and material_obj and active_material:
            active_material.assign_material(context, material_obj, index, event.alt)

    def draw_handler(self, context):
        if hash(context.area) == self.start_area_hash:
            active_material = context.scene.material_helper_property.active_material
            if active_material is None:
                return
            material = active_material.material
            if (active_material is not None) and (material is not None):
                self.draw_material(material)
                self.draw_handler_texts(material)

    def draw_handler_texts(self, material):
        (pick_result, pick_material_obj, pick_material, pick_index) = self.pick_info
        x, y = self.offset + Vector((50, 0))
        with gpu.matrix.push_pop():
            blf.position(0, 0, 0, 1)
            gpu.matrix.translate((x, y))
            text = pgettext_iface("Assign material") + ": " + self.pick_hub_text(material.name)
            if pick_material_obj and pick_material_obj.type == "MESH":
                material_index = from_face_index_get_material_index(pick_material_obj, pick_index)
                slot_name = pgettext_iface("Material slot")
                text += f"({slot_name} {material_index})"
            texts = [text, ]
            if pick_material:
                texts.append(pgettext_iface("Replace material") + f" {pick_material.name}")
            event = self.event
            if event.alt:
                texts.append(pgettext_iface("Assign object material"))
            if event.ctrl:
                texts.append(pgettext_iface("Continuous assign material"))

            self.draw_text_list(texts)

    def pick_hub_text(self, name) -> str:
        text = name
        (result, material_obj, material, index) = self.pick_info
        if result:
            if material is not None:
                text += f" -> {material_obj.name}"
        return text
