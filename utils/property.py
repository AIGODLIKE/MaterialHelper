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


def __set_color_ramp__(prop, data):
    """
    bpy.types.ColorRamp
    TODO
    """
    ...
    # for i in prop.values():
    #     prop.remove(i)


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
                if type(prop) == bpy.types.ColorRamp:
                    # print(prop, type(prop), pr, value, typ, path)
                    __set_color_ramp__(pr, value)
                else:
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
                    pro = __collection_data__(pro, exclude, reversal, only_set)
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
                if isinstance(pro, Iterable) and type(pro) not in (str, dict):
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
