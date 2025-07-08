# version = 1.0.0
import json

exclude_items = {"rna_type", "bl_idname", "srna"}  # 排除项

from collections.abc import Iterable

import bpy
from mathutils import Euler, Vector, Matrix, Color


def __set_collection_data__(prop, data):
    """设置集合值

    Args:
        prop (_type_): _description_
        data (_type_): _description_
    """
    for i in data:
        pro = prop.add()
        set_property(pro, data[i])


def __set_prop__(prop, path, value):
    """设置单个属性"""
    pr = getattr(prop, path, None)
    if pr is not None or path in prop.bl_rna.properties:
        pro = prop.bl_rna.properties[path]
        typ = pro.type
        try:
            if typ == "POINTER":
                set_property(pr, value)
            elif typ == "COLLECTION":
                __set_collection_data__(pr, value)
            elif typ == "ENUM" and pro.is_enum_flag:
                # 可多选枚举
                setattr(prop, path, set(value))
            else:
                setattr(prop, path, value)
        except Exception as e:
            print("ERROR", typ, pro, value, e)
            import traceback
            traceback.print_stack()
            traceback.print_exc()


def set_property(prop, data: dict):
    """version"""
    for k, item in data.items():
        pr = getattr(prop, k, None)
        if pr is not None or k in prop.bl_rna.properties:
            __set_prop__(prop, k, item)


def set_property_to_kmi_properties(properties: "bpy.types.KeyMapItem.properties", props) -> None:
    """注入operator property
    在绘制项时需要使用此方法
    set operator property
    self.operator_property:
    """

    def _for_set_prop(prop, pro, pr):
        for index, j in enumerate(pr):
            try:
                getattr(prop, pro)[index] = j
            except Exception as e:
                print(e.args)

    for pro in props:
        pr = props[pro]
        if hasattr(properties, pro):
            if pr is tuple:
                # 阵列参数
                _for_set_prop(properties, pro, pr)
            else:
                try:
                    setattr(properties, pro, props[pro])
                except Exception as e:
                    print(e.args)


def __collection_data__(prop, exclude=(), reversal=False, only_set=False) -> dict:
    """获取输入集合属性的内容

    Args:
        prop (_type_): _description_

    Returns:
        :param prop:
        :param reversal:
        :param exclude:
    """
    data = {}
    for index, value in enumerate(prop):
        if value not in exclude_items:
            data[index] = get_property(value, exclude, reversal, only_set)
    return data


def get_property(prop, exclude=(), reversal=False, only_set=False) -> dict:
    """
    获取输入的属性内容
    可多选枚举(ENUM FLAG)将转换为列表 list(用于json写入,json 没有 set类型)
    集合信息将转换为字典 index当索引保存  dict

    Args:
        prop (bl_property): 输入blender的属性内容
        exclude (tuple): 排除内容
        reversal (bool): 反转排除内容,如果为True,则只搜索exclude
        only_set (bool): 仅被设置的属性
    Returns:
        dict: 反回字典式数据,
    """
    data = {}
    bl_rna = prop.bl_rna
    for pr in bl_rna.properties:
        try:
            identifier = pr.identifier
            is_ok = (identifier in exclude) if reversal else (identifier not in exclude)

            is_exclude = identifier not in exclude_items
            if is_exclude and is_ok:
                typ = pr.type

                pro = getattr(prop, identifier, None)
                if pro is None:
                    continue

                is_array = False
                if typ == "POINTER":
                    pro = get_property(pro, exclude, reversal, only_set)
                elif typ == "COLLECTION":
                    pro = __collection_data__(pro, exclude, reversal)
                elif typ == "ENUM" and pr.is_enum_flag:
                    # 可多选枚举
                    pro = list(pro)
                elif typ == "FLOAT" and pr.subtype == "COLOR" and type(pro) != float:
                    # color
                    pro = pro[:]
                    is_array = True
                elif isinstance(pro, (Euler, Vector, bpy.types.bpy_prop_array, Color)):
                    pro = pro[:]
                    is_array = True
                elif isinstance(pro, Matrix):
                    res = ()
                    for j in pro:
                        res += (*tuple(j[:]),)
                    is_array = True
                    pro = res

                # 将浮点数设置位数
                if isinstance(pro, Iterable) and type(pro) != str:
                    pro = [round(i, 2) if type(i) == float else i for i in pro][:]
                if isinstance(pro, float):
                    pro = round(pro, 2)

                if only_set:  # and typ not in ("POINTER", "COLLECTION") #去掉默认值,只有被修改了的值列出
                    default_value = getattr(pr, "default", None)
                    if is_array:
                        default_value = list(getattr(pr, "default_array", None))

                    if default_value == pro:
                        continue
                if type(pro) in (set, dict, list, tuple) and len(pro) == 0:  # 去掉空的数据
                    continue
                # print(identifier, default_value, pro, "\t", default_value == pro, type(pro))
                data[identifier] = pro
        except Exception as e:
            print(prop, pr)
            print(e.args)
            import traceback
            traceback.print_exc()
    return data


def get_kmi_property(kmi):
    return dict(
        get_property(
            kmi,
            exclude=(
                "name", "id", "show_expanded", "properties", "idname", "map_type", "active", "propvalue",
                "shift_ui", "ctrl_ui", "alt_ui", "oskey_ui", "is_user_modified", "is_user_defined"
            )
        )
    )


def get_property_enum_items(cls, prop_name) -> list:
    res = []
    for item in cls.properties[prop_name].enum_items:
        res.append((item.identifier, item.name, item.description))
    return res


def get_material_nodes(material: bpy.types.Material) -> dict:
    node_exclude = (
        "outputs",
        "color_tag",
        "type",
        "name",
        "node_tree",
        "nodes",
        "links",
        "location_absolute",
        "warning_propagation",
        "bl_description",
        "bl_height_default",
        "bl_height_max",
        "bl_height_min",
        "bl_icon",
        "bl_label",
        "bl_rna",
        "bl_static_type",
        "bl_width_default",
        "bl_width_max",
        "bl_width_min",
        "inputs",
        "input_template",
        "internal_links",
        "is_active_output",
        "output_template",
        "poll",
        "poll_instance",
        "rna_type",
        "show_options",
        "show_preview",
        "debug_zone_body_lazy_function_graph",
        "debug_zone_lazy_function_graph",
        "draw_buttons",
        "draw_buttons_ext",
        "description",
        "dimensions",
        # "data_type",
        "is_output",
    )

    def get_inputs_info(inputs):
        res = {}
        for ind, inp in enumerate(inputs):
            value = get_property(inp, exclude=("default_value",), reversal=True, only_set=True)
            if value:
                res[ind] = value
        return res

    # exclude_node_inputs = ("links",
    #                        "node",
    #                        "display_shape",
    #                        "dimensions",
    #                        "link_limit",
    #                        "is_multi_input",
    #                        "is_unavailable",
    #                        "pin_gizmo",
    #                        "color_tag",
    #                        "show_texture"
    #                        "is_linked",
    #                        "identifier",
    #                        "distribution",
    #                        "bl_subtype_label",
    #                        "is_output",
    #                        )

    nodes = {}
    for index, node in enumerate(material.node_tree.nodes):
        item = {
            **get_property(node, exclude=node_exclude, only_set=True)
        }
        if inputs_info := get_inputs_info(node.inputs):
            item["inputs"] = inputs_info
        item["bl_idname"] = node.bl_idname
        if item:
            nodes[index] = item
    return nodes


def get_material_links(material: bpy.types.Material):
    ...


def export_material(material: bpy.types.Material):
    nodes_info = get_material_nodes(material)
    links_info = get_material_links(material)
    material_info = get_property(material, exclude=(
        "pass_index",
        "name",
        "displacement_method",
        "use_transparent_shadow",
        "diffuse_color",
        "metallic",
        "roughness",
        "use_backface_culling",
        "use_backface_culling_shadow",
        "use_backface_culling_lightprobe_volume",
        "max_vertex_displacement",
        "surface_render_method",
        "use_raytrace_refraction",
        "thickness_mode",
        "use_thickness_from_shadow",
        "volume_intersection_method",

        "cycles",
        "emission_sampling",
        "use_bump_map_correction",
        "volume_sampling",
        "volume_interpolation",
        "homogeneous_volume",
        "volume_step_rate",

        "lineart",
        "use_material_mask",
        "use_material_mask_bits",
        "mat_occlusion",
        "use_intersection_priority_override",
        "intersection_priority",
    ), reversal=True, only_set=True)
    return {
        **material_info,
        "node_tree": {
            "nodes": nodes_info,
            "links":links_info,
        }
    }


def import_material(material):
    ...


if __name__ == "__main__":
    import os

    print("AA")
    for mat in bpy.data.materials:
        aa = export_material(bpy.context.object.data.materials[0])
        out_file = os.path.join(r"C:\Development\Blender Addon\MaterialHelper\src\material", f"{mat.name.upper()}.json")
        with open(out_file, "w+") as wf:
            wf.writelines(json.dumps(aa, indent=2))
    print()
