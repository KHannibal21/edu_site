import random
from functools import reduce
from typing import Tuple, Dict, Any
from django.db.models import QuerySet
from .models import *

class ImmutableCourse:
    def __init__(self, course: Course):
        self.id = course.id
        self.title = course.title
        self.topics = tuple(course.topics)

class ImmutableItem:
    def __init__(self, item: Item):
        self.id = item.id
        self.lesson_id = item.lesson.id if item.lesson else None
        self.type = item.type
        self.stem = item.stem
        self.options = tuple(item.options) if item.options else ()
        self.answer = tuple(item.answer) if isinstance(item.answer, list) else item.answer
        self.tags = tuple(item.tags) if item.tags else ()
        self.difficulty = item.difficulty

class ImmutableQuizBlueprint:
    def __init__(self, blueprint: QuizBlueprint):
        self.id = blueprint.id
        self.lesson_id = blueprint.lesson.id if blueprint.lesson else None
        self.rules = blueprint.rules

def load_immutable_data() -> Tuple[Tuple[Any, ...], ...]:
    """Загрузка данных в иммутабельные структуры"""
    courses = tuple(ImmutableCourse(course) for course in Course.objects.all())
    items = tuple(ImmutableItem(item) for item in Item.objects.all())
    blueprints = tuple(ImmutableQuizBlueprint(bp) for bp in QuizBlueprint.objects.all())
    users = tuple(User.objects.all())
    return courses, items, blueprints, users

def filter_items_by_difficulty(items: Tuple[ImmutableItem, ...], difficulty_range: Tuple[int, int]) -> Tuple[ImmutableItem, ...]:
    """Фильтрация по сложности с использованием filter"""
    return tuple(filter(lambda item: difficulty_range[0] <= item.difficulty <= difficulty_range[1], items))

def filter_items_by_topics(items: Tuple[ImmutableItem, ...], topics: Tuple[str, ...]) -> Tuple[ImmutableItem, ...]:
    """Фильтрация по темам"""
    if not topics:
        return items
    return tuple(filter(lambda item: any(topic in item.tags for topic in topics), items))

def filter_items_by_type(items: Tuple[ImmutableItem, ...], item_types: Tuple[str, ...]) -> Tuple[ImmutableItem, ...]:
    """Фильтрация по типам заданий"""
    if not item_types:
        return items
    return tuple(filter(lambda item: item.type in item_types, items))

def pick_items_functional(items: Tuple[ImmutableItem, ...], bp: ImmutableQuizBlueprint) -> Tuple[ImmutableItem, ...]:
    """Функциональный подход к выбору заданий"""
    rules = bp.rules
    difficulty = rules.get("difficulty", (1, 5))
    if isinstance(difficulty, list):
        difficulty = (difficulty[0], difficulty[-1])
    count = rules.get("count", 10)
    topics = tuple(rules.get("topics", []))
    item_types = tuple(rules.get("types", []))
    mix = rules.get("mix", False)

    # Композиция фильтров через последовательное применение
    filtered = filter_items_by_difficulty(items, difficulty)
    filtered = filter_items_by_topics(filtered, topics)
    filtered = filter_items_by_type(filtered, item_types)

    # Уникальные ID для избежания дубликатов
    unique_ids = frozenset(item.id for item in filtered)
    unique_items = tuple(item for item in filtered if item.id in unique_ids)

    if mix:
        selected = tuple(random.sample(unique_items, min(count, len(unique_items))))
    else:
        selected = unique_items[:count]

    return selected

def create_quiz_functional(user: User, bp: QuizBlueprint, items_tuple: Tuple[ImmutableItem, ...]) -> Quiz:
    """Создание квиза с функциональным подходом"""
    immutable_bp = ImmutableQuizBlueprint(bp)
    selected_items = pick_items_functional(items_tuple, immutable_bp)

    # Создаем квиз
    quiz_id = f"quiz_{random.randint(1000, 9999)}"
    quiz = Quiz.objects.create(
        id=quiz_id,
        user=user,
        blueprint=bp,
        status="started"
    )

    # Получаем Django объекты Item по ID
    item_ids = [item.id for item in selected_items]
    django_items = Item.objects.filter(id__in=item_ids)
    quiz.items.set(django_items)

    return quiz

def calculate_statistics() -> Dict[str, Any]:
    """Функциональный расчет статистики"""
    items = Item.objects.all()
    courses = Course.objects.all()
    lessons = Lesson.objects.all()
    users = User.objects.all()

    # Распределение по типам с использованием reduce
    type_distribution = reduce(
        lambda acc, item: {**acc, item.type: acc.get(item.type, 0) + 1},
        items,
        {}
    )

    # Распределение по сложности
    difficulty_distribution = reduce(
        lambda acc, item: {**acc, item.difficulty: acc.get(item.difficulty, 0) + 1},
        items,
        {}
    )

    # Уникальные теги
    all_tags = reduce(
        lambda acc, item: acc.union(set(item.tags)),
        items,
        set()
    )

    # Средняя сложность
    total_difficulty = reduce(lambda acc, item: acc + item.difficulty, items, 0)
    avg_difficulty = total_difficulty / len(items) if items else 0

    return {
        'total_courses': len(courses),
        'total_lessons': len(lessons),
        'total_items': len(items),
        'total_users': len(users),
        'type_distribution': type_distribution,
        'difficulty_distribution': difficulty_distribution,
        'unique_tags': tuple(all_tags),
        'avg_difficulty': round(avg_difficulty, 2)
    }

# Функции высшего порядка (HOF)
def create_filter_factory(**filters):
    """Фабрика функций-фильтров"""
    def filter_function(item):
        for key, value in filters.items():
            if key == 'difficulty_range' and not (value[0] <= item.difficulty <= value[1]):
                return False
            elif key == 'topics' and value and not any(topic in item.tags for topic in value):
                return False
            elif key == 'types' and value and item.type not in value:
                return False
        return True
    return filter_function

def apply_filters(items: Tuple[ImmutableItem, ...], *filters) -> Tuple[ImmutableItem, ...]:
    """Применение цепочки фильтров"""
    return tuple(filter(lambda item: all(f(item) for f in filters), items))

def sum_score(grades: Tuple[Grade, ...]) -> float:
    """Сумма баллов через reduce"""
    return reduce(lambda acc, grade: acc + grade.score, grades, 0.0)