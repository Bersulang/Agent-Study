"""真实pypdf文件解析；--self-test使用临时PDF，不需要下载业务资料。"""
import argparse
import json
from pathlib import Path
import tempfile

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


def parse_pdf(path):
    rows, errors = [], []
    reader = PdfReader(path)
    if reader.is_encrypted:
        raise ValueError("加密PDF需授权解密，不自动尝试密码")
    for number, page in enumerate(reader.pages, 1):
        try:
            # extract_text只能读取文本层；空结果必须报告，不能假装内容为空政策。
            text = (page.extract_text() or "").strip()
            if not text:
                errors.append({"page": number, "reason": "no_text_layer_or_blank", "next": "检查页面，必要时OCR"})
            else:
                rows.append({"source": str(Path(path).resolve()), "page": number, "text": text})
        except Exception as error:
            # 页级错误保持可追踪，其他页仍可解析；正式工程应进一步限定异常类型。
            errors.append({"page": number, "reason": type(error).__name__})
    return {"pages": rows, "errors": errors}


def self_test():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "fixture.pdf"
        writer = PdfWriter()
        page = writer.add_blank_page(width=300, height=200)
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                                 NameObject("/Subtype"): NameObject("/Type1"),
                                 NameObject("/BaseFont"): NameObject("/Helvetica")})
        page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})})
        stream = DecodedStreamObject()
        stream.set_data(b"BT /F1 12 Tf 20 100 Td (Receipt required.) Tj ET")
        page[NameObject("/Contents")] = writer._add_object(stream)
        writer.add_blank_page(width=300, height=200)
        with path.open("wb") as output:
            writer.write(output)
        result = parse_pdf(path)
        assert result["pages"][0]["text"] == "Receipt required."
        assert result["errors"][0]["page"] == 2
        print("真实PDF文本提取通过；空白页正确进入质量错误列表")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="解析PDF并保留页码来源")
    parser.add_argument("file", nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.file:
        print(json.dumps(parse_pdf(args.file), ensure_ascii=False, indent=2))
    else:
        parser.error("请提供PDF路径或--self-test")
