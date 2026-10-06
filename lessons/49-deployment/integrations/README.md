# 实际HTTP与Docker接入

从项目根目录运行本地服务（此命令常驻，Ctrl+C停止）：

```powershell
New-Item -ItemType Directory -Force artifacts/service-data
.\.venv\Scripts\python.exe lessons/49-deployment/integrations/server.py
```

另一个终端检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8080/health/live
Invoke-RestMethod http://127.0.0.1:8080/health/ready
```

在已安装Docker的环境，使用：

```powershell
docker compose -f lessons/49-deployment/integrations/compose.yaml up --build -d
docker compose -f lessons/49-deployment/integrations/compose.yaml ps
docker compose -f lessons/49-deployment/integrations/compose.yaml down
```

`down`不删除命名卷；不要加`-v`，那会删除卷数据。卷权限取决于部署平台，若目录不可写，检查容器用户UID与卷初始化权限，禁止直接改成特权模式。

这是健康机制小服务，不是完整Agent后端。本机无Docker，未声称容器运行通过。真正Agent服务见阶段39与56。根目录验证脚本不自动启动容器。
