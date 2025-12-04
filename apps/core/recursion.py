"""
Лаба №2 - Рекурсия
Рекурсивные функции для обработки иерархических структур
"""
from typing import Tuple, Dict, Any, List, Union, Optional
from .models import Course, Lesson, Item, QuizBlueprint


def flatten_curriculum(
        courses: Tuple[Course, ...],
        lessons: Tuple[Lesson, ...],
        acc: Optional[List[Tuple[str, str]]] = None
) -> Tuple[Tuple[str, str], ...]:
    """
    Рекурсивное уплощение учебного плана
    Возвращает кортеж пар (course_id, lesson_id)

    Args:
        courses: кортеж курсов
        lessons: кортеж уроков
        acc: аккумулятор (используется в рекурсии)

    Returns:
        Кортеж пар курс-урок
    """
    if acc is None:
        acc = []

    # Базовый случай: нет курсов
    if not courses:
        return tuple(acc)

    # Рекурсивный случай: обрабатываем первый курс
    current_course = courses[0]
    remaining_courses = courses[1:]

    # Находим все уроки этого курса
    course_lessons = [lesson for lesson in lessons if lesson.course_id == current_course.id]

    # Добавляем пары в аккумулятор
    for lesson in course_lessons:
        acc.append((current_course.id, lesson.id))

    # Рекурсивный вызов для остальных курсов
    return flatten_curriculum(remaining_courses, lessons, acc)


def build_item_tree(
        items: Tuple[Item, ...],
        topic: str,
        depth: int = 0,
        max_depth: int = 3
) -> Tuple[Dict[str, Any], ...]:
    """
    Рекурсивное построение дерева вопросов по теме
    Группирует вопросы по тегам -> по сложности

    Args:
        items: все вопросы
        topic: тема для фильтрации
        depth: текущая глубина рекурсии
        max_depth: максимальная глубина

    Returns:
        Кортеж узлов дерева
    """
    if depth >= max_depth or not items:
        return tuple()

    # Фильтруем вопросы по теме
    topic_items = [item for item in items if item.topic == topic]

    if not topic_items:
        return tuple()

    # Группируем по первому тегу (если есть)
    tag_groups: Dict[str, List[Item]] = {}

    for item in topic_items:
        if item.tags:
            primary_tag = item.tags[0]
            if primary_tag not in tag_groups:
                tag_groups[primary_tag] = []
            tag_groups[primary_tag].append(item)
        else:
            # Вопросы без тегов попадают в отдельную группу
            if "untagged" not in tag_groups:
                tag_groups["untagged"] = []
            tag_groups["untagged"].append(item)

    # Строим дерево рекурсивно
    tree_nodes = []

    for tag, tag_items in tag_groups.items():
        # Группируем вопросы по сложности
        diff_groups: Dict[int, List[Item]] = {}
        for item in tag_items:
            diff = item.difficulty.value
            if diff not in diff_groups:
                diff_groups[diff] = []
            diff_groups[diff].append(item)

        # Создаем узел для этого тега
        node = {
            "tag": tag,
            "depth": depth,
            "item_count": len(tag_items),
            "difficulty_groups": {}
        }

        # Добавляем группы сложности
        for diff, diff_items in diff_groups.items():
            node["difficulty_groups"][diff] = {
                "count": len(diff_items),
                "items": tuple(diff_items)
            }

        # Рекурсивно строим поддеревья для других тем, на которые ссылаются теги
        if depth < max_depth - 1 and tag != "untagged":
            # Находим связанные темы через теги
            related_topics = set()
            for item in tag_items:
                # Ищем вопросы с таким же тегом, но в других темах
                for other_item in items:
                    if other_item.topic != topic and tag in other_item.tags:
                        related_topics.add(other_item.topic)

            # Рекурсивно строим поддеревья для связанных тем
            subtrees = []
            for related_topic in related_topics:
                subtree = build_item_tree(items, related_topic, depth + 1, max_depth)
                if subtree:
                    subtrees.append({
                        "topic": related_topic,
                        "subtrees": subtree
                    })

            if subtrees:
                node["related_topics"] = tuple(subtrees)

        tree_nodes.append(node)

    return tuple(tree_nodes)


def walk_blueprint_rules(
        rules: Dict[str, Any],
        path: str = "",
        acc: Optional[List[Tuple[str, Union[str, int, bool, float]]]] = None
) -> Tuple[Tuple[str, Union[str, int, bool, float]], ...]:
    """
    Рекурсивный обход вложенных правил blueprint
    Разворачивает в плоский список пар (путь, значение)

    Args:
        rules: словарь правил (возможно вложенный)
        path: текущий путь (для рекурсии)
        acc: аккумулятор результатов

    Returns:
        Кортеж пар (путь, значение)
    """
    if acc is None:
        acc = []

    for key, value in rules.items():
        current_path = f"{path}.{key}" if path else key

        if isinstance(value, dict):
            # Рекурсивный вызов для вложенного словаря
            walk_blueprint_rules(value, current_path, acc)
        elif isinstance(value, (list, tuple)):
            # Обрабатываем списки/кортежи
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    walk_blueprint_rules(item, f"{current_path}[{i}]", acc)
                else:
                    acc.append((f"{current_path}[{i}]", item))
        else:
            # Примитивное значение
            acc.append((current_path, value))

    return tuple(acc)


def count_items_recursive(
        items: Tuple[Item, ...],
        predicate,
        count: int = 0
) -> int:
    """
    Рекурсивный подсчет вопросов, удовлетворяющих предикату

    Args:
        items: вопросы для проверки
        predicate: функция-предикат (Item -> bool)
        count: текущий счетчик (для рекурсии)

    Returns:
        Количество вопросов, удовлетворяющих предикату
    """
    # Базовый случай: пустой список
    if not items:
        return count

    # Рекурсивный случай
    first_item = items[0]
    remaining_items = items[1:]

    if predicate(first_item):
        return count_items_recursive(remaining_items, predicate, count + 1)
    else:
        return count_items_recursive(remaining_items, predicate, count)


def find_item_by_id_recursive(
        items: Tuple[Item, ...],
        item_id: str
) -> Optional[Item]:
    """
    Рекурсивный поиск вопроса по ID

    Args:
        items: вопросы для поиска
        item_id: ID для поиска

    Returns:
        Найденный Item или None
    """
    # Базовый случай 1: пустой список
    if not items:
        return None

    # Базовый случай 2: нашли элемент
    if items[0].id == item_id:
        return items[0]

    # Рекурсивный случай
    return find_item_by_id_recursive(items[1:], item_id)