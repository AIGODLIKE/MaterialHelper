import bpy

from . import zh_CN
from ...utils import get_language_list


def get_language(language):
    if language not in get_language_list():
        if bpy.app.version < (4, 0, 0):
            return "zh_CN"
        else:
            return "zh_HANS"
    return language


class TranslationHelper:
    def __init__(self, name: str, data: dict, lang='zh_CN'):
        self.name = name
        self.translations_dict = dict()

        for src, src_trans in data.items():
            key = ("Operator", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans
            key = ("*", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans

    def register(self):
        try:
            bpy.app.translations.register(self.name, self.translations_dict)
        except ValueError as e:
            print(e.args)

    def unregister(self):
        bpy.app.translations.unregister(self.name)


MaterialHelper_zh_HANS = TranslationHelper("Material_zh_HANS", zh_CN.data, lang=get_language("zh_HANS"))


def register():
    MaterialHelper_zh_HANS.register()


def unregister():
    MaterialHelper_zh_HANS.unregister()
