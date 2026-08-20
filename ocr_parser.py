def extract_text(result):

    lines = []

    try:
        for block in result["text"]:
            for text_block in block["blocks"]:
                for line in text_block["textLines"]:
                    lines.append(line["value"])

    except Exception as e:
        print("OCR解析失败:", e)

    return "\n".join(lines)