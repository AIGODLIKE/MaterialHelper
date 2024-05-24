import os

import bpy
from pathlib import Path
from .op_edit_material_asset import get_local_selected_assets, tag_redraw

C_TMP_ASSET_TAG = 'tmp_asset_mathp'

_uuid = '11451419-1981-0aaa-aaaa-aaaaaaaaaaaa'


class selectedAsset:
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_assets') and context.selected_assets

def is_cat_find_in_file(path, uuid=_uuid):
    # with open(path, 'r', encoding='utf-8') as f:
    #     for line in f.readlines():
    #         print(line)
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f.readlines()):
            if line.startswith(("#", "VERSION", "\n")):
                continue
            uuid = line.split(":")[0]
            # print(uuid)
            if uuid != _uuid: continue
            return i
    print('Material Helper: Category not found in file')
    return False


def append_asset_cats_txt(path):
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f"{_uuid}:Material Helper:Material Helper\n")
    except Exception as e:
        print(e)


def get_asset_cats_txt():
    # D:\SteamLibrary\steamapps\common\Blender\3.6\datafiles\assets
    blender_dir = Path(bpy.app.binary_path).parent
    version = bpy.app.version
    version_str = f"{version[0]}.{version[1]}"
    asset_cats_txt = blender_dir.joinpath(version_str, "datafiles", 'assets', 'blender_assets.cats.txt')

    if not asset_cats_txt.exists():
        asset_cats_txt.touch()
        with open(asset_cats_txt, "w", encoding='utf-8') as f:
            f.write("""# This is an Asset Catalog Definition file for Blender.
#
# Empty lines and lines starting with `#` will be ignored.
# The first non-ignored line should be the version indicator.
# Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"

VERSION 1
""")

    return asset_cats_txt


# def remove_asset_cats_txt(uuid=_uuid):
#     asset_cats_txt = get_asset_cats_txt()
#     line_index = is_cat_find_in_file(asset_cats_txt)
#     try:
#         if line_index is not None:
#             # remove line at line index
#             with open(asset_cats_txt, 'r', encoding='utf-8') as f:
#                 lines = f.readlines()
#             with open(asset_cats_txt, 'w', encoding='utf-8') as f:
#                 for i, line in enumerate(lines):
#                     if i == line_index: continue
#                     f.write(line)
#     except Exception as e:
#         print(e)


def ensure_curent_file_asset_cats():
    if bpy.data.filepath == '':
        print("Material Helper: File Not Save! Set category failed")
        return None

    cat_path = Path(bpy.data.filepath).parent.joinpath('blender_assets.cats.txt')
    cat_path_mod = Path(bpy.data.filepath).parent.joinpath('blender_assets.cats.txt~')

    if cat_path_mod.exists():  # delete
        cat_path_mod.unlink()

    if cat_path.exists():
        if not is_cat_find_in_file(cat_path):
            print('Material Helper: Writing category to current file')
            append_asset_cats_txt(cat_path)
    else:
        with open(cat_path, "w", encoding='utf-8') as f:
            print('Material Helper Creating Category')
            f.write("""# This is an Asset Catalog Definition file for Blender.
#
# Empty lines and lines starting with `#` will be ignored.
# The first non-ignored line should be the version indicator.
# Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"

VERSION 1

11451419-1981-0aaa-aaaa-aaaaaaaaaaaa:Material Helper:Material Helper
""")


# def ensure_asset_cats_txt():
#     asset_cats_txt = get_asset_cats_txt()
#     if not is_cat_find_in_file(asset_cats_txt):
#         try:
#             append_asset_cats_txt(asset_cats_txt)
#         except Exception as e:
#             print(e)


class MATHP_OT_set_category(bpy.types.Operator):
    bl_idname = 'mathp.set_category'
    bl_label = 'Set Category'

    target_catalog: bpy.props.StringProperty(name="Target Catalog", default="Material Helper")

    def execute(self, context):
        # objs = get_local_selected_assets(context)
        if bpy.data.filepath == '':
            return {'CANCELLED'}

        ensure_curent_file_asset_cats()

        for mat in bpy.data.materials:
            if mat.asset_data is None: continue
            if C_TMP_ASSET_TAG in mat.asset_data.tags:
                if mat.asset_data.catalog_id != _uuid:
                    mat.asset_data.catalog_id = _uuid
        try:
            bpy.ops.asset.library_refresh()
        except Exception as e:
            print(e)
        tag_redraw()

        return {'FINISHED'}


def register():
    pass


def unregister():
    pass
