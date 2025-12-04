"""
Лаба №5 - Ленивые вычисления
Потоковая обработка данных с использованием генераторов
"""
from typing import Iterable, Iterator, Tuple, List, Dict, Any, Callable
from datetime import datetime

from .models import Answer, Item, Rule, Grade
from .containers import Either


def iter_answers(
    answers: Tuple[Answer, ...],
    predicate: Callable[[Answer], bool]
) -> Iterable[Answer]:
    """
    Ленивая итерация по ответам с фильтрацией

    Args:
        answers: кортеж ответов
        predicate: функция-предикат для фильтрации

    Yields:
        Ответы, удовлетворяющие предикату
    """
    for answer in answers:
        if predicate(answer):
            yield answer


def lazy_grade_stream(
    items: Tuple[Item, ...],
    answers: Iterable[Answer],
    rules: Tuple[Rule, ...],
    negative_marking: bool = False
) -> Iterator[Tuple[str, float]]:
    """
    Ленивый стрим оценок (item_id, score)

    Args:
        items: вопросы
        answers: итерируемый объект с ответами
        rules: правила оценки
        negative_marking: учитывать ли штрафы

    Yields:
        Пары (item_id, score) по мере обработки
    """
    # Создаем словарь для быстрого поиска вопросов
    items_dict = {item.id: item for item in items}

    for answer in answers:
        item = items_dict.get(answer.item_id)

        if not item:
            # Если вопрос не найден, возвращаем 0
            yield (answer.item_id, 0.0)
            continue

        # Упрощенная оценка (в реальности должна использовать validation.grade_item)
        try:
            # Ищем правило для типа вопроса
            applicable_rules = [
                rule for rule in rules
                if rule.condition.get("type") == item.type.value
            ]

            if applicable_rules:
                rule = applicable_rules[0]
                score = rule.apply(item, answer)

                if negative_marking and score == 0:
                    penalty = rule.action.get("penalty", 0)
                    score = -penalty
            else:
                # Правило по умолчанию
                score = 1.0 if answer.content.get("is_correct", False) else 0.0

            yield (item.id, score)

        except Exception:
            yield (item.id, 0.0)


def materialize_stream(
    stream: Iterator[Tuple[str, float]],
    limit: int = None
) -> List[Tuple[str, float]]:
    """
    Материализация ленивого стрима с ограничением

    Args:
        stream: ленивый стрим
        limit: максимальное количество элементов

    Returns:
        Список материализованных пар
    """
    result = []

    for i, item in enumerate(stream):
        if limit is not None and i >= limit:
            break
        result.append(item)

    return result


def calculate_top_k(
    stream: Iterator[Tuple[str, float]],
    k: int = 5
) -> List[Tuple[str, float]]:
    """
    Ленивое вычисление top-K вопросов по сложности оценки

    Args:
        stream: стрим (item_id, score)
        k: количество топовых элементов

    Returns:
        Список топ-K вопросов
    """
    from heapq import nlargest

    # Используем временное хранилище для стрима
    scores_dict = {}

    for item_id, score in stream:
        if item_id not in scores_dict:
            scores_dict[item_id] = []
        scores_dict[item_id].append(score)

    # Вычисляем средний балл для каждого вопроса
    avg_scores = [
        (item_id, sum(scores) / len(scores))
        for item_id, scores in scores_dict.items()
    ]

    # Возвращаем топ-K
    return nlargest(k, avg_scores, key=lambda x: x[1])


def lazy_statistics(
    stream: Iterator[Tuple[str, float]]
) -> Dict[str, Any]:
    """
    Ленивое вычисление статистики по стриму оценок

    Args:
        stream: стрим (item_id, score)

    Returns:
        Словарь со статистикой
    """
    total = 0
    count = 0
    min_score = float('inf')
    max_score = float('-inf')
    scores = []

    for _, score in stream:
        total += score
        count += 1
        min_score = min(min_score, score)
        max_score = max(max_score, score)
        scores.append(score)

    if count == 0:
        return {
            "count": 0,
            "total": 0,
            "average": 0,
            "min": 0,
            "max": 0,
            "std_dev": 0
        }

    average = total / count

    # Стандартное отклонение (лениво, но требует хранения всех значений)
    if len(scores) > 1:
        variance = sum((x - average) ** 2 for x in scores) / (len(scores) - 1)
        std_dev = variance ** 0.5
    else:
        std_dev = 0

    return {
        "count": count,
        "total": total,
        "average": round(average, 2),
        "min": round(min_score, 2),
        "max": round(max_score, 2),
        "std_dev": round(std_dev, 2)
    }


def batch_process_stream(
    stream: Iterator[Tuple[str, float]],
    batch_size: int = 10
) -> Iterator[List[Tuple[str, float]]]:
    """
    Разбиение стрима на батчи

    Args:
        stream: исходный стрим
        batch_size: размер батча

    Yields:
        Батчи данных
    """
    batch = []

    for item in stream:
        batch.append(item)

        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch:
        yield batch


def real_time_score_tracker(
    answers_stream: Iterable[Answer],
    items: Tuple[Item, ...],
    rules: Tuple[Rule, ...]
) -> Iterator[Dict[str, Any]]:
    """
    Трекер реального времени для онлайн-подсчета результатов

    Args:
        answers_stream: стрим ответов
        items: вопросы
        rules: правила

    Yields:
        Обновленная статистика после каждого ответа
    """
    total_score = 0.0
    answered_count = 0
    correct_count = 0
    items_dict = {item.id: item for item in items}

    for answer in answers_stream:
        item = items_dict.get(answer.item_id)

        if item:
            # Упрощенная оценка
            is_correct = answer.content.get("is_correct", False)
            score = 1.0 if is_correct else 0.0

            total_score += score
            answered_count += 1

            if is_correct:
                correct_count += 1

            accuracy = correct_count / answered_count if answered_count > 0 else 0
            avg_score = total_score / answered_count if answered_count > 0 else 0

            yield {
                "timestamp": datetime.now().isoformat(),
                "answer_id": answer.id,
                "item_id": answer.item_id,
                "score": score,
                "total_score": total_score,
                "answered_count": answered_count,
                "correct_count": correct_count,
                "accuracy": round(accuracy, 3),
                "average_score": round(avg_score, 3),
                "completion_percentage": min(100, (answered_count / len(items)) * 100)
            }