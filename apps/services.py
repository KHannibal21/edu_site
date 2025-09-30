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
    """Загрузка данных в иммутабельные структуры с map"""
    courses = tuple(map(ImmutableCourse, Course.objects.all()))
    items = tuple(map(ImmutableItem, Item.objects.all()))
    blueprints = tuple(map(ImmutableQuizBlueprint, QuizBlueprint.objects.all()))
    users = tuple(User.objects.all())
    return courses, items, blueprints, users


def filter_items_by_difficulty(items: Tuple[ImmutableItem, ...], difficulty_range: Tuple[int, int]):
    """Фильтрация по сложности через filter"""
    return tuple(filter(lambda item: difficulty_range[0] <= item.difficulty <= difficulty_range[1], items))


def filter_items_by_topics(items: Tuple[ImmutableItem, ...], topics: Tuple[str, ...]):
    """Фильтрация по темам через filter"""
    if not topics:
        return items
    return tuple(filter(lambda item: any(topic in item.tags for topic in topics), items))


def filter_items_by_type(items: Tuple[ImmutableItem, ...], item_types: Tuple[str, ...]):
    """Фильтрация по типам через filter"""
    if not item_types:
        return items
    return tuple(filter(lambda item: item.type in item_types, items))


def pick_items_functional(items: Tuple[ImmutableItem, ...], bp: ImmutableQuizBlueprint):
    """Выбор заданий (filter + map)"""
    rules = bp.rules
    difficulty = rules.get("difficulty", (1, 5))
    if isinstance(difficulty, list):
        difficulty = (difficulty[0], difficulty[-1])
    count = rules.get("count", 10)
    topics = tuple(rules.get("topics", []))
    item_types = tuple(rules.get("types", []))
    mix = rules.get("mix", False)

    filtered = filter_items_by_difficulty(items, difficulty)
    filtered = filter_items_by_topics(filtered, topics)
    filtered = filter_items_by_type(filtered, item_types)

    # map для вытаскивания id
    unique_ids = frozenset(map(lambda item: item.id, filtered))
    unique_items = tuple(filter(lambda item: item.id in unique_ids, filtered))

    if mix:
        return tuple(random.sample(unique_items, min(count, len(unique_items))))
    return unique_items[:count]


def create_quiz_functional(user: User, bp: QuizBlueprint, items_tuple: Tuple[ImmutableItem, ...]) -> Quiz:
    """Создание квиза (map + filter)"""
    immutable_bp = ImmutableQuizBlueprint(bp)
    selected_items = pick_items_functional(items_tuple, immutable_bp)

    quiz_id = f"quiz_{random.randint(1000, 9999)}"
    quiz = Quiz.objects.create(id=quiz_id, user=user, blueprint=bp, status="started")

    # map → список id
    item_ids = list(map(lambda item: item.id, selected_items))
    django_items = Item.objects.filter(id__in=item_ids)
    quiz.items.set(django_items)

    return quiz


def calculate_statistics() -> Dict[str, Any]:
    """Статистика с reduce"""
    items = Item.objects.all()
    courses = Course.objects.all()
    lessons = Lesson.objects.all()
    users = User.objects.all()

    type_distribution = reduce(
        lambda acc, item: {**acc, item.type: acc.get(item.type, 0) + 1},
        items,
        {}
    )
    difficulty_distribution = reduce(
        lambda acc, item: {**acc, item.difficulty: acc.get(item.difficulty, 0) + 1},
        items,
        {}
    )
    all_tags = reduce(
        lambda acc, item: acc.union(set(item.tags)),
        items,
        set()
    )
    total_difficulty = reduce(lambda acc, item: acc + item.difficulty, items, 0)
    avg_difficulty = total_difficulty / len(items) if items else 0

    return {
        "total_courses": len(courses),
        "total_lessons": len(lessons),
        "total_items": len(items),
        "total_users": len(users),
        "type_distribution": type_distribution,
        "difficulty_distribution": difficulty_distribution,
        "unique_tags": tuple(all_tags),
        "avg_difficulty": round(avg_difficulty, 2),
    }


def create_filter_factory(**filters):
    """Фабрика фильтров"""
    def filter_function(item):
        for key, value in filters.items():
            if key == "difficulty_range" and not (value[0] <= item.difficulty <= value[1]):
                return False
            elif key == "topics" and value and not any(topic in item.tags for topic in value):
                return False
            elif key == "types" and value and item.type not in value:
                return False
        return True
    return filter_function


def apply_filters(items: Tuple[ImmutableItem, ...], *filters):
    """Цепочка фильтров через filter"""
    return tuple(filter(lambda item: all(f(item) for f in filters), items))


def sum_score(grades: Tuple[Grade, ...]) -> float:
    """Сумма баллов через reduce"""
    return reduce(lambda acc, grade: acc + grade.score, grades, 0.0)


def by_topic(topic: str):
    """Замыкание: фильтр по теме"""

    def topic_filter(item):
        return topic in item.tags

    return topic_filter


def by_difficulty(lo: int, hi: int):
    """Замыкание: фильтр по диапазону сложности"""

    def difficulty_filter(item):
        return lo <= item.difficulty <= hi

    return difficulty_filter


def by_type(qtype: str):
    """Замыкание: фильтр по типу задания"""

    def type_filter(item):
        return item.type == qtype

    return type_filter


def with_tags(required: Tuple[str, ...]):
    """Замыкание: фильтр по набору тегов (все должны присутствовать)"""

    def tags_filter(item):
        return all(tag in item.tags for tag in required)

    return tags_filter


def create_composite_filter(*filters):
    """Замыкание: композиция нескольких фильтров"""

    def composite_filter(item):
        return all(filter_func(item) for filter_func in filters)

    return composite_filter


# ==================== ЗАМЫКАНИЯ-КОНФИГУРАТОРЫ ====================

def quiz_configurator(base_count: int = 10):
    """Замыкание: конфигуратор квизов с настройками по умолчанию"""

    def configure_quiz(**overrides):
        config = {
            'count': base_count,
            'difficulty_range': (1, 5),
            'required_types': ('mcq/single', 'mcq/multi', 'short'),
            'mix_questions': True,
            'time_limit': None
        }
        config.update(overrides)
        return config

    return configure_quiz


def difficulty_preset(preset_name: str):
    """Замыкание: предустановки сложности"""
    presets = {
        'easy': (1, 2),
        'medium': (2, 4),
        'hard': (4, 5),
        'exam': (3, 5)
    }

    def get_preset():
        return presets.get(preset_name, (1, 5))

    return get_preset


# ==================== PIPELINE ФУНКЦИИ ====================

def create_filter_pipeline(*filter_creators):
    """Создание пайплайна фильтров через замыкания"""

    def pipeline_creator(**kwargs):
        filters = []
        for creator in filter_creators:
            if callable(creator):
                filters.append(creator(**kwargs))
        return create_composite_filter(*filters)

    return pipeline_creator


# Готовые пайплайны
basic_pipeline = create_filter_pipeline(
    lambda **kw: by_difficulty(kw.get('min_difficulty', 1), kw.get('max_difficulty', 5)),
    lambda **kw: by_type(kw.get('qtype', '')) if kw.get('qtype') else (lambda x: True)
)

advanced_pipeline = create_filter_pipeline(
    lambda **kw: by_difficulty(kw.get('min_difficulty', 1), kw.get('max_difficulty', 5)),
    lambda **kw: by_topic(kw.get('topic', '')) if kw.get('topic') else (lambda x: True),
    lambda **kw: with_tags(kw.get('required_tags', ())) if kw.get('required_tags') else (lambda x: True)
)