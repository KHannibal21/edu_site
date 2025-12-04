"""
Лаба №4 - Валидация и оценка с использованием Maybe/Either
"""
from typing import Tuple, Dict, Any, Optional
from datetime import datetime

from .models import Item, Answer, Rule, Quiz
from .containers import Maybe, Either, pipeline


def safe_item(items: Tuple[Item, ...], item_id: str) -> Maybe[Item]:
    """
    Безопасное получение вопроса по ID

    Args:
        items: кортеж вопросов
        item_id: ID искомого вопроса

    Returns:
        Maybe[Item]: Just(item) если найден, иначе Nothing
    """
    for item in items:
        if item.id == item_id:
            return Maybe.just(item)
    return Maybe.nothing()


def validate_answer(
        item: Item,
        answer: Answer,
        rules: Tuple[Rule, ...]
) -> Either[Dict[str, Any], Answer]:
    """
    Валидация ответа с использованием Either

    Args:
        item: вопрос
        answer: ответ пользователя
        rules: правила валидации

    Returns:
        Either[Dict, Answer]: Right(answer) если валиден, Left(ошибки) если нет
    """
    errors = {}

    # Проверка соответствия типа вопроса
    if answer.content.get("type") != item.type.value:
        errors["type_mismatch"] = f"Expected {item.type.value}, got {answer.content.get('type')}"

    # Проверка наличия обязательных полей
    required_fields = ["content"]
    if item.type.value in ["multiple_choice", "single_choice"]:
        required_fields.append("selected")

    for field in required_fields:
        if field not in answer.content:
            errors[f"missing_{field}"] = f"Required field '{field}' is missing"

    # Проверка по специфичным правилам
    for rule in rules:
        if rule.condition.get("type") == item.type.value:
            # Здесь может быть дополнительная валидация
            pass

    if errors:
        return Either.left({
            "item_id": item.id,
            "answer_id": answer.id,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        })

    return Either.right(answer)


def grade_item(
        item: Item,
        answer: Answer,
        rules: Tuple[Rule, ...],
        negative_marking: bool = False
) -> Either[Dict[str, Any], float]:
    """
    Оценка ответа с поддержкой negative_marking

    Args:
        item: вопрос
        answer: ответ пользователя
        rules: правила оценки
        negative_marking: учитывать ли штрафы за неправильные ответы

    Returns:
        Either[Dict, float]: Right(оценка) если успешно, Left(ошибка) если нет
    """
    try:
        # Ищем правило для этого типа вопроса
        applicable_rules = [
            rule for rule in rules
            if rule.condition.get("type") == item.type.value
        ]

        if not applicable_rules:
            return Either.left({
                "error": "no_rules",
                "message": f"No grading rules for item type: {item.type.value}",
                "item_id": item.id
            })

        # Применяем первое подходящее правило
        rule = applicable_rules[0]
        score = rule.apply(item, answer)

        # Применяем negative marking если нужно
        if negative_marking and score == 0:
            penalty = rule.action.get("penalty", 0)
            score = -penalty

        # Ограничиваем оценку разумными пределами
        max_score = rule.action.get("max", 1)
        min_score = rule.action.get("min", -1 if negative_marking else 0)
        score = max(min_score, min(max_score, score))

        return Either.right(score)

    except Exception as e:
        return Either.left({
            "error": "grading_failed",
            "message": str(e),
            "item_id": item.id,
            "answer_id": answer.id
        })


def process_attempt_pipeline(
        items: Tuple[Item, ...],
        answers: Tuple[Answer, ...],
        rules: Tuple[Rule, ...],
        negative_marking: bool = False
) -> Either[Dict[str, Any], Tuple[Dict[str, float], float]]:
    """
    Полный пайплайн обработки попытки с использованием Maybe/Either

    Args:
        items: вопросы квиза
        answers: ответы пользователя
        rules: правила оценки
        negative_marking: учитывать ли штрафы

    Returns:
        Either с результатами оценки или ошибкой
    """
    # Создаем пайплайн с использованием композиции контейнеров
    from .containers import pipeline

    def process_single_answer(item_answer_pair):
        item, answer = item_answer_pair

        # Пайплайн: валидация -> оценка
        process = pipeline(
            lambda x: validate_answer(x[0], x[1], rules),
            lambda valid_answer: grade_item(item, valid_answer, rules, negative_marking)
        )

        return process((item, answer))

    # Собираем пары вопрос-ответ
    results = []
    total_score = 0.0

    for answer in answers:
        # Находим соответствующий вопрос
        item_maybe = safe_item(items, answer.item_id)

        if item_maybe.is_nothing():
            return Either.left({
                "error": "item_not_found",
                "item_id": answer.item_id,
                "answer_id": answer.id
            })

        item = item_maybe.get_or_else(None)

        # Обрабатываем пару
        result = process_single_answer((item, answer))

        if result.is_left():
            # Если ошибка - возвращаем её
            return result.map_left(lambda err: {
                **err,
                "context": f"Failed to process answer {answer.id} for item {item.id}"
            })

        # Добавляем результат
        score = result.get_or_else(0)
        results.append((item.id, score))
        total_score += score

    # Преобразуем в итоговый формат
    details = {item_id: score for item_id, score in results}

    return Either.right((details, total_score))


def create_grade_from_results(
        quiz: Quiz,
        user_id: str,
        details: Dict[str, float],
        total_score: float
) -> Either[Dict[str, Any], Any]:  # Здесь должен быть тип Grade, но пока Any
    """
    Создание объекта Grade из результатов оценки

    Args:
        quiz: квиз
        user_id: ID пользователя
        details: детализированные оценки по вопросам
        total_score: общая оценка

    Returns:
        Either с Grade или ошибкой
    """
    try:
        # Вычисляем максимальный возможный балл
        max_score = len(quiz.items)  # Упрощенно: 1 балл за вопрос

        # Создаем ID для оценки
        grade_id = f"grade_{quiz.id}_{user_id}_{datetime.now().isoformat()}"

        # В реальности здесь нужно импортировать и создать Grade
        # grade = Grade(grade_id, quiz.id, user_id, total_score, max_score, details)

        return Either.right({
            "grade_id": grade_id,
            "quiz_id": quiz.id,
            "user_id": user_id,
            "score": total_score,
            "max_score": max_score,
            "percentage": (total_score / max_score * 100) if max_score > 0 else 0,
            "details": details,
            "created_at": datetime.now().isoformat()
        })

    except Exception as e:
        return Either.left({
            "error": "grade_creation_failed",
            "message": str(e),
            "quiz_id": quiz.id,
            "user_id": user_id
        })