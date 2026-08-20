import os
import json
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed

from ocr_client import OcrInterface
from ocr_parser import extract_text


SRC_DIR = "src"
JSON_DIR = "dst/json"
TXT_DIR = "dst/txt"


def process_single_image(filename):
    try:
        ocr = OcrInterface()

        image_path = os.path.join(SRC_DIR, filename)

        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(
                f.read()
            ).decode("utf-8")

        result = ocr.get_ocr(image_base64)

        name = os.path.splitext(filename)[0]

        with open(
            os.path.join(JSON_DIR, name + ".json"),
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                result,
                f,
                ensure_ascii=False,
                indent=2
            )

        text = extract_text(result)

        with open(
            os.path.join(TXT_DIR, name + ".txt"),
            "w",
            encoding="utf-8"
        ) as f:
            f.write(text)

        return filename, True, None

    except Exception as e:
        return filename, False, str(e)



def process_images():

    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(TXT_DIR, exist_ok=True)

    image_ext = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp"
    }

    files = [
        f for f in os.listdir(SRC_DIR)
        if os.path.splitext(f)[1].lower() in image_ext
    ]

    print(f"共发现 {len(files)} 张图片")


    # 线程数量根据OCR服务能力调整
    max_workers = 8

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        futures = [
            executor.submit(
                process_single_image,
                filename
            )
            for filename in files
        ]


        for future in as_completed(futures):

            filename, success, error = future.result()

            if success:
                print("完成:", filename)
            else:
                print(
                    "失败:",
                    filename,
                    error
                )


if __name__ == "__main__":
    process_images()