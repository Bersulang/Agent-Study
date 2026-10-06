# 实际集成验证

2026-10-06，Windows PowerShell + Python 3.12.10。

实际安装环境为系统临时目录下agent-study-sdk-17-29，未改全局Python。安装固定顶层依赖：pypdf6.19.0、langgraph1.2.13、mcp2.3.0。

## 可复现命令

安装命令见README.md；从项目根目录，用安装依赖后的虚拟环境解释器执行：

```powershell
.\.venv\Scripts\python.exe lessons\27-langgraph\integrations\langgraph_demo.py
```

实际退出码：0

```text
paused {'task': 'T1', 'action': '生成只读报告'}
resumed {'task': 'T1', 'approved': False, 'status': 'rejected'}
accepted {'task': 'T2', 'approved': True, 'status': 'done'}
```

同进程InMemorySaver、interrupt拒绝恢复、另一线程批准与条件边子图通过，未验证持久存储或业务写入。

课程集成验证不等于学员能力已通过。完整独立环境依赖快照见同目录verified-environment.txt；教学安装仍以requirements.txt为准。
