"""
Лаба №2 - Лямбда и замыкания
Замыкания-фильтры для отбора вопросов
"""
from typing import Callable, Tuple
from functools import partial

from .models import Item, ItemType, Difficulty


def by_topic(topic: str) -> Callable[[Item], bool]:
    """
    Замыкание: создает функцию-фильтр по теме

    Args:
        topic: требуемая тема

    Returns:
        Функция, принимающая Item и возвращающая bool
    """

    def filter_func(item: Item) -> bool:
        return item.topic == topic

    return filter_func


def by_difficulty(lo: int, hi: int) -> Callable[[Item], bool]:
    """
    Замыкание: фильтр по диапазону сложности

    Args:
        lo: минимальная сложность
        hi: максимальная сложность

    Returns:
        Функция-фильтр
    """

    def filter_func(item: Item) -> bool:
        return lo <= item.difficulty.value <= hi

    return filter_func


def by_type(qtype: ItemType) -> Callable[[Item], bool]:
    """
    Замыкание: фильтр по типу вопроса

    Args:
        qtype: тип вопроса (ItemType enum)

    Returns:
        Функция-фильтр
    """

    def filter_func(item: Item) -> bool:
        return item.type == qtype

    return filter_func


def with_tags(required: Tuple[str, ...]) -> Callable[[Item], bool]:
    """
    Замыкание: фильтр по обязательным тегам
    Все указанные теги должны присутствовать

    Args:
        required: кортеж обязательных тегов

    Returns:
        Функция-фильтр
    """

    def filter_func(item: Item) -> bool:
        return all(tag in item.tags for tag in required)

    return filter_func


def with_any_tags(any_of: Tuple[str, ...]) -> Callable[[Item], bool]:
    """
    Замыкание: фильтр по любому из тегов

    Args:
        any_of: кортеж тегов (хотя бы один должен быть)

    Returns:
        Функция-фильтр
    """

    def filter_func(item: Item) -> bool:
        return any(tag in item.tags for tag in any_of)

    return filter_func


def create_complex_filter(
        topic: str = None,
        difficulty_range: Tuple[int, int] = None,
        qtype: ItemType = None,
        required_tags: Tuple[str, ...] = None,
        any_tags: Tuple[str, ...] = None
) -> Callable[[Item], bool]:
    """
    Фабрика сложных фильтров (композиция замыканий)

    Args:
        topic: фильтр по теме
        difficulty_range: (min, max)
        qtype: фильтр по типу
        required_tags: обязательные теги
        any_tags: хотя бы один из тегов

    Returns:
        Комбинированная функция-фильтр
    """
    filters = []

    if topic:
        filters.append(by_topic(topic))

    if difficulty_range:
        lo, hi = difficulty_range
        filters.append(by_difficulty(lo, hi))

    if qtype:
        filters.append(by_type(qtype))

    if required_tags:
        filters.append(with_tags(required_tags))

    if any_tags:
        filters.append(with_any_tags(any_tags))

    def combined_filter(item: Item) -> bool:
        """Применяет все фильтры через AND"""
        return all(f(item) for f in filters)

    return combined_filter


# Предопределенные фильтры (частичное применение)
easy_items = partial(by_difficulty, 1, 2)
medium_items = partial(by_difficulty, 3, 3)
hard_items = partial(by_difficulty, 4, 5)

multiple_choice_only = partial(by_type, ItemType.MULTIPLE_CHOICE)
coding_only = partial(by_type, ItemType.CODE)


def apply_filters_chain(
        items: Tuple[Item, ...],
        *filters: Callable[[Item], bool]
) -> Tuple[Item, ...]:
    """
    Применение цепочки фильтров к вопросам

    Args:
        items: исходные вопросы
        *filters: последовательность функций-фильтров

    Returns:
        Отфильтрованные вопросы
    """
    result = items

    for filter_func in filters:
        result = tuple(filter(filter_func, result))

    return result