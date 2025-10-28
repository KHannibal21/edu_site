import random
from functools import reduce
from typing import Tuple, Dict, Any, List
from django.db.models import QuerySet
from .models import *
from .ftypes import Maybe, Either

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


# ==================== LAB 4: FUNCTIONAL PATTERNS ====================

def safe_item(items: Tuple[ImmutableItem, ...], item_id: str) -> Maybe[ImmutableItem]:
    """Безопасное получение задания по ID"""
    for item in items:
        if item.id == item_id:
            return Maybe(item)
    return Maybe(None)


def validate_answer(item: ImmutableItem, answer_payload: Any, rules: Tuple[Rule, ...]) -> Either[Dict, Any]:
    """Валидация ответа с использованием Either"""

    # Проверяем наличие negative_marking правила
    negative_marking = any(rule.kind == 'negative_marking' for rule in rules)

    try:
        # Валидация в зависимости от типа задания
        if item.type in ('mcq/single', 'mcq/multi'):
            if not isinstance(answer_payload, (list, tuple)):
                return Either.left({"error": "Answer should be list/tuple for MCQ"})

            if item.type == 'mcq/single' and len(answer_payload) != 1:
                return Either.left({"error": "Single choice should have exactly one answer"})

            # Проверяем что индексы в пределах options
            if any(idx >= len(item.options) for idx in answer_payload):
                return Either.left({"error": "Answer index out of bounds"})

        elif item.type == 'short':
            if not isinstance(answer_payload, str):
                return Either.left({"error": "Short answer should be string"})


        elif item.type == 'numeric':

            # Пытаемся преобразовать строку в число

            try:

                # Если это строка - преобразуем в число

                if isinstance(answer_payload, str):
                    # Убираем возможные кавычки и пробелы

                    cleaned = answer_payload.strip().strip('"').strip("'")

                    answer_payload = float(cleaned) if '.' in cleaned else int(cleaned)

                if not isinstance(answer_payload, (int, float)):
                    return Either.left({"error": "Numeric answer should be number"})

            except (ValueError, TypeError):

                return Either.left({"error": "Numeric answer should be a valid number"})

        return Either.right(answer_payload)

    except Exception as e:
        return Either.left({"error": f"Validation error: {str(e)}"})


def grade_item(item: ImmutableItem, answer_payload: Any, rules: Tuple[Rule, ...]) -> Either[Dict, float]:
    """Оценка задания с поддержкой negative_marking"""

    # Получаем validated answer
    validated_answer = validate_answer(item, answer_payload, rules)

    # Если валидация не прошла - возвращаем ошибку
    if validated_answer.is_left():
        return validated_answer

    # Проверяем negative_marking
    negative_marking = any(
        rule.kind == 'negative_marking' and rule.payload.get('enabled', False)
        for rule in rules
    )

    try:
        score = 0.0

        if item.type in ('mcq/single', 'mcq/multi'):
            # Сравниваем ответы (предполагаем что answer - это кортеж правильных индексов)
            user_answer = set(validated_answer.get_or_else([]))
            correct_answer = set(item.answer)

            if user_answer == correct_answer:
                score = 1.0
            elif negative_marking and user_answer:  # Частично правильный с negative marking
                correct_selected = len(user_answer.intersection(correct_answer))
                incorrect_selected = len(user_answer - correct_answer)
                penalty = incorrect_selected * 0.25  # Штраф за неправильные
                score = max(0.0, (correct_selected / len(correct_answer)) - penalty)

        elif item.type == 'short':
            # Простая проверка (в реальности нужна более сложная логика)
            user_answer = validated_answer.get_or_else("").strip().lower()
            correct_answer = str(item.answer[0]).strip().lower() if item.answer else ""
            score = 1.0 if user_answer == correct_answer else 0.0

        elif item.type == 'numeric':
            user_answer = float(validated_answer.get_or_else(0))
            correct_answer = float(item.answer[0]) if item.answer else 0.0
            score = 1.0 if abs(user_answer - correct_answer) < 0.001 else 0.0

        return Either.right(round(score, 2))

    except Exception as e:
        return Either.left({"error": f"Grading error: {str(e)}"})


def grade_quiz_pipeline(
        quiz: Quiz,
        answers: Dict[str, Any],
        items_tuple: Tuple[ImmutableItem, ...],
        rules: Tuple[Rule, ...]
) -> Either[Dict, Grade]:
    """Пайплайн проверки попытки → подсчет score → создание Grade"""

    breakdown = []
    total_score = 0.0
    processed_items = 0

    for item_id, answer_payload in answers.items():
        # Шаг 1: Безопасное получение задания
        item_maybe = safe_item(items_tuple, item_id)

        # Шаг 2: Если задание найдено - оцениваем его
        grade_result = item_maybe.bind(
            lambda item: grade_item(item, answer_payload, rules)
        )

        # Шаг 3: Обрабатываем результат оценки
        if isinstance(grade_result, Maybe) and grade_result.is_nothing():
            # Задание не найдено
            breakdown.append((item_id, 0.0))
        elif isinstance(grade_result, Either):
            if grade_result.is_right():
                item_score = grade_result.get_or_else(0.0)
                total_score += item_score
                breakdown.append((item_id, item_score))
                processed_items += 1
            else:
                # Ошибка при оценке - считаем 0 баллов
                breakdown.append((item_id, 0.0))

    # Вычисляем итоговый score
    final_score = total_score / max(processed_items, 1)

    try:
        # Создаем Grade объект
        grade = Grade.objects.create(
            id=f"grade_{quiz.id}",
            quiz=quiz,
            score=round(final_score, 2),
            breakdown=breakdown
        )
        return Either.right(grade)
    except Exception as e:
        return Either.left({"error": f"Failed to create grade: {str(e)}"})


# Утилиты для демонстрации
def demonstrate_maybe_either(items_tuple: Tuple[ImmutableItem, ...]) -> Dict[str, Any]:
    """Демонстрация работы Maybe/Either"""

    # Демонстрация Maybe
    existing_item = safe_item(items_tuple, "item_1")
    non_existing_item = safe_item(items_tuple, "non_existent")

    maybe_demo = {
        "existing_item": existing_item.map(lambda x: x.type).get_or_else("not_found"),
        "non_existing_item": non_existing_item.map(lambda x: x.type).get_or_else("not_found"),
        "existing_repr": repr(existing_item),
        "non_existing_repr": repr(non_existing_item)
    }

    # Демонстрация Either
    sample_item = items_tuple[0] if items_tuple else None
    if sample_item:
        valid_answer = [0] if sample_item.options else []
        invalid_answer = "wrong_type"

        valid_validation = validate_answer(sample_item, valid_answer, ())
        invalid_validation = validate_answer(sample_item, invalid_answer, ())

        either_demo = {
            "valid_validation": repr(valid_validation),
            "invalid_validation": repr(invalid_validation),
            "valid_score": grade_item(sample_item, valid_answer, ()).get_or_else(0.0),
            "invalid_score": grade_item(sample_item, invalid_answer, ()).get_or_else(0.0)
        }
    else:
        either_demo = {"error": "No items available"}

    return {
        "maybe_demo": maybe_demo,
        "either_demo": either_demo
    }


def demonstrate_interactive_maybe_either(items: Tuple[ImmutableItem, ...], item_id: str, answer_data: Any) -> Dict[
    str, Any]:
    """Интерактивная демонстрация Maybe/Either"""

    # Maybe демонстрация
    maybe_result = safe_item(items, item_id)

    # Either демонстрация
    selected_item = maybe_result.get_or_else(items[0] if items else None)
    validation_result = None
    grading_result = None

    if selected_item:
        validation_result = validate_answer(selected_item, answer_data, ())
        grading_result = grade_item(selected_item, answer_data, ())

    return {
        'item_id': item_id,
        'maybe_result': maybe_result,
        'validation_result': validation_result,
        'grading_result': grading_result,
        'selected_item': selected_item
    }