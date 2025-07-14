import os

material_list = {}

def register():
    folder = os.path.dirname(__file__)
    for file in os.listdir(folder):
        if file.endswith(".json"):
            name = file.replace(".json", "")
            file_path = os.path.join(folder, file)
            material_list[name] = file_path


def unregister():
    material_list.clear()
