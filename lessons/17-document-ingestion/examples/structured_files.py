"""标准库读取Markdown标题与CSV表格；保留结构而非只拼接所有单元格。"""
import csv
import io


def markdown_sections(text):
    heading, rows = "未命名", []
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        elif line.strip():
            rows.append({"heading": heading, "line": number, "text": line})
    return rows


def table_rows(text):
    # DictReader把第一行当列名；保留列名可避免800到底代表限额还是人数的歧义。
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != ["department", "limit"]:
        raise ValueError("表格列不符合department,limit契约")
    rows = []
    for number, row in enumerate(reader, 2):
        if None in row or not row["department"] or not row["limit"]:
            raise ValueError("表格列数或必填字段异常")
        rows.append({"row": number, "department": row["department"], "limit": int(row["limit"])})
    return rows


if __name__ == "__main__":
    print(markdown_sections("# 交通费\n需要发票\n# 住宿费\n限额800"))
    print(table_rows("department,limit\nENG,800\nHR,500\n"))
