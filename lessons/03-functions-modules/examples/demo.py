"""业务模块与运行入口分离；同目录rules可直接导入。"""
from rules import select, add_tag

def main():
    records = [{"id": "T1", "priority": 5}, {"id": "T2", "priority": 2}]
    print(f"筛选：{select(records, minimum=4)}")
    print(f"首次标签：{add_tag('urgent')}")
    print(f"第二次标签：{add_tag('review')}")

if __name__ == "__main__":
    main()
