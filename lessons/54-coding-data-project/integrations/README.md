# 执行沙箱的工程延伸

默认代码只运行已经审查的固定教学程序。`-I`、超时与目录白名单不是OS沙箱。

在有Docker的隔离测试机中，可对复制到独立目录的教学脚本使用如下约束（不要挂载真实项目、SSH目录、凭证或Docker socket）：

```powershell
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --memory 128m --cpus 0.5 --pids-limit 32 --user 10001:10001 python:3.12-slim python -I -c "print(2 + 3)"
```

这里只执行固定表达式，不接受模型任意构造整个shell命令。本机无Docker，命令未实跑。生产还需镜像固定digest、隔离节点、资源清理、输出限制和任务身份，不保证容器能防御所有内核漏洞。

SQL生产接入使用真正只读账户、查询超时、行数限制、租户过滤和禁止扩展/外部连接；不要只用SELECT开头判断查询安全。
