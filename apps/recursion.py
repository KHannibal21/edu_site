from typing import Tuple, Dict, Any, List, Union
from .models import Course, Lesson, Item


# ==================== РЕКУРСИВНЫЕ ФУНКЦИИ ====================

def flatten_curriculum(courses: Tuple[Course, ...], lessons: Tuple[Lesson, ...]) -> Tuple[Tuple[str, str], ...]:
    """
    Рекурсивное преобразование иерархии курсов и уроков в плоскую структуру
    Возвращает кортеж кортежей (course_title, lesson_title)
    """

    def _flatten_course(course: Course, acc: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        # Рекурсивно обрабатываем уроки курса
        course_lessons = [lesson for lesson in lessons if lesson.course_id == course.id]

        for lesson in course_lessons:
            acc.append((course.title, lesson.title))

        return acc

    def _process_courses(courses_list: Tuple[Course, ...], accumulator: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        # Базовый случай рекурсии
        if not courses_list:
            return accumulator

        # Обрабатываем первый курс
        first_course = courses_list[0]
        _flatten_course(first_course, accumulator)

        # Рекурсивный вызов для оставшихся курсов
        return _process_courses(courses_list[1:], accumulator)

    result = _process_courses(courses, [])
    return tuple(result)


def build_item_tree(items: Tuple[Item, ...], topic: str) -> Tuple[Dict[str, Any], ...]:
    """
    Рекурсивное построение дерева заданий по темам
    Возвращает кортеж словарей с иерархической структурой
    """

    def _build_branch(current_items: Tuple[Item, ...], current_topic: str, level: int = 0) -> Dict[str, Any]:
        # Базовый случай рекурсии
        if not current_items:
            return {}

        # Фильтруем задания по текущей теме
        topic_items = [item for item in current_items if current_topic in item.tags]
        other_items = [item for item in current_items if current_topic not in item.tags]

        # Рекурсивно строим поддеревья для подтем
        subtopics = set()
        for item in other_items:
            for tag in item.tags:
                if tag != current_topic:
                    subtopics.add(tag)

        subtrees = []
        for subtopic in subtopics:
            subtree = _build_branch(tuple(other_items), subtopic, level + 1)
            if subtree:  # Добавляем только непустые поддеревья
                subtrees.append(subtree)

        return {
            'topic': current_topic,
            'level': level,
            'items': tuple(item.id for item in topic_items),
            'items_count': len(topic_items),
            'subtopics': tuple(subtrees)
        }

    # Запускаем рекурсию с корневой темой
    tree = _build_branch(items, topic)
    return (tree,) if tree else ()


def walk_blueprint_rules(rules: Dict) -> Tuple[Tuple[str, Union[str, int, bool]], ...]:
    """
    Рекурсивный обход вложенных правил blueprint
    Разворачивает все правила в плоский список пар (ключ, значение)
    """

    def _walk(current_rules: Dict, path: str = "", accumulator: List[Tuple[str, Any]] = None) -> List[Tuple[str, Any]]:
        if accumulator is None:
            accumulator = []

        # Базовый случай рекурсии
        if not current_rules:
            return accumulator

        # Обрабатываем первую пару ключ-значение
        key, value = next(iter(current_rules.items()))
        full_key = f"{path}.{key}" if path else key

        if isinstance(value, dict):
            # Рекурсивный вызов для вложенного словаря
            _walk(value, full_key, accumulator)
        elif isinstance(value, (list, tuple)):
            # Обрабатываем списки/кортежи
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    _walk(item, f"{full_key}[{i}]", accumulator)
                else:
                    accumulator.append((f"{full_key}[{i}]", item))
        else:
            # Простое значение
            accumulator.append((full_key, value))

        # Рекурсивный вызов для оставшихся правил
        remaining_rules = {k: v for k, v in current_rules.items() if k != key}
        return _walk(remaining_rules, path, accumulator)

    result = _walk(rules)
    return tuple(result)


# ==================== ВСПОМОГАТЕЛЬНЫЕ РЕКУРСИВНЫЕ ФУНКЦИИ ====================

def count_items_in_tree(tree: Dict[str, Any]) -> int:
    """
    Рекурсивный подсчет всех заданий в дереве (включая поддеревья)
    """
    if not tree:
        return 0

    total = tree.get('items_count', 0)

    # Рекурсивно суммируем задания из поддеревьев
    for subtree in tree.get('subtopics', []):
        total += count_items_in_tree(subtree)

    return total


def find_max_depth(tree: Dict[str, Any], current_depth: int = 0) -> int:
    """
    Рекурсивный поиск максимальной глубины дерева
    """
    if not tree or not tree.get('subtopics'):
        return current_depth

    max_depth = current_depth
    for subtree in tree.get('subtopics', []):
        depth = find_max_depth(subtree, current_depth + 1)
        max_depth = max(max_depth, depth)

    return max_depth