"""完整版本包与发布门槛；本地内存别名不等同生产发布系统。"""
import hashlib
import json

REQUIRED = {"code", "model", "prompt", "tool_schema", "index"}

def fingerprint(bundle):
    if set(bundle) != REQUIRED or any(not isinstance(v, str) or not v for v in bundle.values()):
        raise ValueError("版本包字段缺失或不合法")
    stable = json.dumps(bundle, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(stable.encode()).hexdigest()

def promote(registry, bundle, metrics):
    version = fingerprint(bundle)
    # 所有门槛检查完毕才修改活动版本。
    if metrics["security_violations"] or metrics["success_rate"] < 0.9:
        raise ValueError("候选版本未通过发布门槛")
    registry["versions"][version] = dict(bundle)
    registry["active"] = version
    return version

def rollback(registry, version):
    if version not in registry["versions"]:
        raise ValueError("不能回滚到未知版本")
    registry["active"] = version

if __name__ == "__main__":
    registry = {"versions": {}, "active": None}
    bundle = {key: "v1" for key in REQUIRED}
    old = promote(registry, bundle, {"security_violations": [], "success_rate": 1.0})
    task_version = old
    try:
        promote(registry, {**bundle, "prompt": "v2"}, {"security_violations": ["leak"], "success_rate": 1.0})
    except ValueError as error:
        print("发布拒绝：", error)
    print("旧版本仍活跃：", registry["active"] == old)
    print("任务版本保持：", task_version == old)
