# 教学基线；生产固定镜像digest并定期更新安全补丁。
FROM python:3.12-slim
WORKDIR /app
# 非root用户运行；仅复制服务代码，不复制学习目录中的凭证。
RUN useradd --uid 10001 --create-home learner && mkdir /app/data && chown learner:learner /app/data
COPY integrations/server.py /app/lessons/49-deployment/integrations/server.py
COPY examples/demo.py /app/lessons/49-deployment/examples/demo.py
USER 10001:10001
ENV HOST=0.0.0.0 PORT=8080 DATA_DIR=/app/data
EXPOSE 8080
CMD ["python", "/app/lessons/49-deployment/integrations/server.py"]
