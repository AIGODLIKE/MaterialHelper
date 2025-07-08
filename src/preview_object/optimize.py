import os

folder = os.path.dirname(__file__)
out_folder = os.path.join(folder, "optimize")
for file in os.listdir(folder):
    if file.endswith(".obj"):
        f = os.path.join(folder, file)
        print(f)
        lines = []
        with open(f, "r") as rf:
            for line in rf.readlines():
                l = line.replace(r"\n", "")
                split_list = l.split(" ")
                splits = []
                for li in split_list:
                    if li.count(".") == 1:
                        try:
                            value = round(float(li), 3)  # 小数点
                            splits.append(str(value))
                        except ValueError:
                            splits.append(li)
                    else:
                        splits.append(li)
                new_line = " ".join(splits)
                lines.append(new_line + "\n")

        new_file = os.path.join(out_folder, file)
        with open(new_file, "w+") as wf:
            wf.writelines(lines)
