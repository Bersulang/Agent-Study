"""职责路由：规则模拟意图判断，权限始终由程序验证。"""
def route(text, allowed_roles, model_choice=None):
    # 同时命中两种职责时不猜测，进入人工澄清。
    matches = []
    if "政策" in text:
        matches.append("knowledge")
    if "工单" in text:
        matches.append("ticket")
    role = matches[0] if len(matches) == 1 else "human"
    # 模型输出只是候选；即使候选合法，也不能扩大调用者权限。
    if model_choice is not None:
        role = model_choice if model_choice in {"knowledge", "ticket"} else "human"
    if role not in allowed_roles:
        role = "human"
    return {"role": role, "permission": "read" if role != "human" else "none"}

def run_case(case):
    if case == "knowledge":
        return route("查询退款政策", {"knowledge"})
    if case == "ambiguous":
        return route("政策和工单都要查", {"knowledge", "ticket"})
    if case == "denied":
        return route("查询工单", {"knowledge"}, model_choice="ticket")
    raise ValueError("未知案例")

if __name__ == "__main__":
    # 固定成功与失败场景，运行后退出，不请求模型或启动常驻服务。
    for case in ['knowledge', 'ambiguous', 'denied']:
        print(case, run_case(case))
