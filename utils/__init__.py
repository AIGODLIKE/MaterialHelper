import ast
import re
from typing import Any

import bpy

MATERIAL_HELPER_ASSET_TAG = 'tmp_asset_mathp'
MATERIAL_HELPER_ASSET_UUID = '11451419-1981-0000-0000-000000000000'


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
