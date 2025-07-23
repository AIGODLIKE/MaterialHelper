from pathlib import Path

import bpy

from ..debug import DEBUG_ENSURE_CURRENT_FILE_ASSET_CATS
from ..utils import MATERIAL_HELPER_ASSET_UUID, MATERIAL_HELPER_ASSET_TAG, get_pref, tag_redraw


def cat_uuid_in_file(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f.readlines()):
            if ":" not in line: continue
            uuid = line.split(":")[0]
            if uuid != MATERIAL_HELPER_ASSET_UUID:
                continue
            return i
    return False


def append_asset_cats_txt(path: Path) -> None:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{MATERIAL_HELPER_ASSET_UUID}:Material Helper:Material Helper\n")
    except PermissionError:
        print("Material Helper: Permission Denied")
    except FileNotFoundError:
        print("Material Helper: Category file not found")
    except Exception as e:
        print("Unexpected Error:", e)
    else:
        print("Material Helper: Category file updated")


def select_catalog():
    for win in bpy.data.window_managers[0].windows:
        for area in win.screen.areas:
            for space in area.spaces:
                if space.type == "ASSET":
                    space.params.catalog_id = MATERIAL_HELPER_ASSET_UUID


class AssetSync:
    is_sync = False
    material_count = -1

    @classmethod
    def sync(cls):
        pref = get_pref()
        cls.ensure_current_file_asset_cats()

        if pref.auto_update:
            if not cls.is_sync:
                cls.is_sync = True
                select_catalog()
            if len(bpy.data.materials) != cls.material_count:
                cls.material_sync_asset()
        elif cls.is_sync:  # 关闭同步
            cls.close_sync()

    @classmethod
    def close_sync(cls):
        for mat in bpy.data.materials:
            if mat.asset_data is None:
                continue
            if MATERIAL_HELPER_ASSET_TAG in mat.asset_data.tags:
                mat.asset_clear()

    @classmethod
    def material_sync_asset(cls):
        for mat in bpy.data.materials:
            if mat.asset_data:  # 已经是资产
                continue
            if mat.is_grease_pencil:  # 是GP
                continue

            mat.asset_mark()
            mat.asset_generate_preview()
            mat.asset_data.tags.new(MATERIAL_HELPER_ASSET_TAG)
            mat.asset_data.catalog_id = MATERIAL_HELPER_ASSET_UUID

        tag_redraw()

    @classmethod
    def check_is_sync(cls):
        return get_pref().auto_update and cls.is_sync

    @classmethod
    def ensure_current_file_asset_cats(cls):
        if bpy.data.filepath == "":  # 未保存文件无法写入
            if DEBUG_ENSURE_CURRENT_FILE_ASSET_CATS:
                print("Material Helper: File Not Save! Set category failed")
            return

        cat_path = Path(bpy.data.filepath).parent.joinpath("blender_assets.cats.txt")
        cat_path_mod = Path(bpy.data.filepath).parent.joinpath("blender_assets.cats.txt~")

        if cat_path_mod.exists():  # delete
            cat_path_mod.unlink()

        if cat_path.exists():
            if DEBUG_ENSURE_CURRENT_FILE_ASSET_CATS:
                print("cat_uuid_in_file", cat_uuid_in_file(cat_path))
            if not cat_uuid_in_file(cat_path):
                if DEBUG_ENSURE_CURRENT_FILE_ASSET_CATS:
                    print("Material Helper: Writing category to current file")
                append_asset_cats_txt(cat_path)
        else:
            with open(cat_path, "w+", encoding="utf-8") as f:
                if DEBUG_ENSURE_CURRENT_FILE_ASSET_CATS:
                    print("Material Helper Creating Category")
                f.write(f"""# This is an Asset Catalog Definition file for Blender.
    #
    # Empty lines and lines starting with `#` will be ignored.
    # The first non-ignored line should be the version indicator.
    # Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"

    VERSION 1

    {MATERIAL_HELPER_ASSET_UUID}:Material Helper:Material Helper
    """)
