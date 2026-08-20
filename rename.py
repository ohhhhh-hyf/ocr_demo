import os
import re

SRC_DIR = "src"


def rename_files():
    for filename in os.listdir(SRC_DIR):
        old_path = os.path.join(SRC_DIR, filename)

        if not os.path.isfile(old_path):
            continue

        name, ext = os.path.splitext(filename)

        # 提取天数
        day_match = re.search(r"第(\d+)天", name)
        if not day_match:
            print("跳过(未找到天数):", filename)
            continue

        day = day_match.group(1)

        # 提取最后一个 - 后面的学号
        student_id = name.split("-")[-1]

        new_name = f"{student_id}_{day}{ext}"
        new_path = os.path.join(SRC_DIR, new_name)

        os.rename(old_path, new_path)

        print(f"{filename} -> {new_name}")


if __name__ == "__main__":
    rename_files()