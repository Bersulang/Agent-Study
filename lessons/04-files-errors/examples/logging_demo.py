"""开发者日志演示：不记录完整工单、密钥或异常敏感正文。"""
import json
import logging
import sys


def main():
    logger = logging.getLogger("ticket_import")
    # 日志配置放入口，导入模块时不修改整个应用的root logger。
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    try:
        json.loads("{broken")
    except json.JSONDecodeError:
        # 记录事件和分类，真实系统可增加请求ID，不输出业务全文。
        logger.warning("event=load_failed file_id=teaching-fixture error=json_corrupted")
    finally:
        logger.removeHandler(handler)
        handler.close()


if __name__ == "__main__":
    main()
