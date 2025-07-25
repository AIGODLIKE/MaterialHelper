import ast
import os.path
import re
from typing import Any

import bpy

MATERIAL_HELPER_ASSET_TAG = 'Material Helper temp asset tag'
MATERIAL_HELPER_ASSET_UUID = '11451419-1981-6666-6666-000000000000'


def get_pref() -> bpy.types.AddonPreferences:
    """get preferences of this plugin"""
    from .. import __package__ as base_package
    return bpy.context.preferences.addons.get(base_package).preferences


def get_language_list() -> Any | None:
    """
    v1.1
    Traceback (most recent call last):
  File "<blender_console>", line 1, in <module>
TypeError: bpy_struct: item.attr = val: enum "a" not found in ('DEFAULT', 'en_US', 'es', 'ja_JP', 'sk_SK', 'vi_VN', 'zh_HANS', 'ar_EG', 'de_DE', 'fr_FR', 'it_IT', 'ko_KR', 'pt_BR', 'pt_PT', 'ru_RU', 'uk_UA', 'zh_TW', 'ab', 'ca_AD', 'cs_CZ', 'eo', 'eu_EU', 'fa_IR', 'ha', 'he_IL', 'hi_IN', 'hr_HR', 'hu_HU', 'id_ID', 'ky_KG', 'nl_NL', 'pl_PL', 'sr_RS', 'sr_RS@latin', 'sv_SE', 'th_TH', 'tr_TR')
    """
    try:
        bpy.context.preferences.view.language = ""
    except TypeError as e:
        matches = re.findall(r'\(([^()]*)\)', e.args[-1])
        return ast.literal_eval(f"({matches[-1]})")
    return None


def get_icon(icon: str) -> int:
    from ..src.icons import previews_icons
    return previews_icons.get(icon.lower()).icon_id


def get_local_selected_assets(context):
    """获取选择的本地资产
    :param context: bpy.context
    :return: 选择项里的本地资产(任何资产类型) bpy.types.Object/Material/World
    """
    cur_lib_name = context.area.spaces.active.params.asset_library_reference

    match_obj = [asset_file.local_id for asset_file in context.selected_assets if
                 cur_lib_name in {"LOCAL", "ALL"}]

    return match_obj


def get_fbx_path(name):
    """获取预览文件的fbx路径"""
    folder = os.path.dirname(os.path.dirname(__file__))
    fbx_folder = os.path.join(folder, "src", "preview_object")
    file_name = f"{name.upper()}.fbx"
    file_path = os.path.join(fbx_folder, file_name)
    if not os.path.exists(file_path):
        return os.path.join(fbx_folder, "SHADERBALL.fbx")
    return file_path


def tag_redraw():
    """所有区域重绘制更新"""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            for region in area.regions:
                region.tag_redraw()

def is_blender_close() -> bool:
    import sys
    import traceback
    for stack in traceback.extract_stack(sys._getframe().f_back, limit=None):
        if stack.name == "disable_all" and stack.line == "disable(mod_name)":
            return True
    return False