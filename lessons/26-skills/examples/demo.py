# 按需加载的能力包：默认标准库、离线、有限退出。
SKILLS = {
    "report": {"version": "1.0", "trigger": "报告", "permission": "read",
               "instructions": "读取工单；汇总数量；使用中文模板；标注来源。"},
    "cleanup": {"version": "1.0", "trigger": "清理", "permission": "delete",
                "instructions": "列出待删除文件；取得明确授权；验证路径后执行。"},
}

def discover(task):
    # 这里只匹配摘要，不执行包里的文本或脚本。
    return [name for name, meta in SKILLS.items() if meta["trigger"] in task]

def load(name, permissions):
    if name not in SKILLS:
        raise KeyError("未知能力包")
    meta = SKILLS[name]
    if meta["permission"] not in permissions:
        raise PermissionError("当前身份没有执行该包的权限")
    return dict(meta)

def main():
    names = discover("生成工单报告")
    print(names)
    print(load(names[0], {"read"}))

if __name__ == "__main__":
    main()
