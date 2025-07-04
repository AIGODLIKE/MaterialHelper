from pathlib import Path
from typing import Union

import bpy

from ..utils import MATERIAL_HELPER_ASSET_UUID


class SelectedAsset:
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_assets') and context.selected_assets


def cat_uuid_in_file(path: Path, uuid: str = MATERIAL_HELPER_ASSET_UUID) -> Union[int, bool]:
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f.readlines()):
            if ":" not in line: continue
            uuid = line.split(":")[0]
            if uuid != MATERIAL_HELPER_ASSET_UUID:
                continue
            return i
    return False


def append_asset_cats_txt(path: Path) -> None:
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f"{MATERIAL_HELPER_ASSET_UUID}:Material Helper:Material Helper\n")
    except PermissionError:
        print('Material Helper: Permission Denied')
    except FileNotFoundError:
        print('Material Helper: Category file not found')
    except Exception as e:
        print('Unexpected Error:', e)


def ensure_current_file_asset_cats():
    if bpy.data.filepath == '':
        print("Material Helper: File Not Save! Set category failed")
        return

    cat_path = Path(bpy.data.filepath).parent.joinpath('blender_assets.cats.txt')
    cat_path_mod = Path(bpy.data.filepath).parent.joinpath('blender_assets.cats.txt~')

    if cat_path_mod.exists():  # delete
        cat_path_mod.unlink()

    if cat_path.exists():
        if not cat_uuid_in_file(cat_path):
            print('Material Helper: Writing category to current file')
            append_asset_cats_txt(cat_path)
    else:
        with open(cat_path, "w", encoding='utf-8') as f:
            print('Material Helper Creating Category')
            f.write(f"""# This is an Asset Catalog Definition file for Blender.
#
# Empty lines and lines starting with `#` will be ignored.
# The first non-ignored line should be the version indicator.
# Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"

VERSION 1

{MATERIAL_HELPER_ASSET_UUID}:Material Helper:Material Helper
""")
