from enum import Enum
from typing import Type, List, Tuple


def as_choices(enum_cls: Type[Enum], use_names: bool = False) -> List[Tuple[str, str]]:
    if use_names:
        return [(choice.value, choice.name) for choice in enum_cls]
    return [(choice.value, choice.value) for choice in enum_cls]
