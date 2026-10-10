"""按阶段注册可重复的学生练习行为检查。"""
from pathlib import Path

from .foundation import build_foundation_cases
from .knowledge import build_knowledge_cases
from .services import build_service_cases
from .advanced import build_advanced_cases


def build_cases(stage: int, lesson_dir: Path) -> list[tuple[str, callable]]:
    """返回某阶段的命名检查；每个检查无参，成功返回None，失败抛异常。"""
    if type(stage) is not int or not 1 <= stage <= 56:
        raise ValueError("stage必须是01到56之间的整数")
    lesson_dir = Path(lesson_dir)
    if 1 <= stage <= 16:
        return build_foundation_cases(stage, lesson_dir)
    if 17 <= stage <= 29:
        return build_knowledge_cases(stage, lesson_dir)
    if 30 <= stage <= 43:
        return build_service_cases(stage, lesson_dir)
    return build_advanced_cases(stage, lesson_dir)


__all__ = ["build_cases"]
