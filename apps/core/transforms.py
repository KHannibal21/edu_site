"""
Лаба №1 - Чистые функции + неизменяемость + HOF
Функции высшего порядка: map, filter, reduce
"""
import json
from typing import Tuple, Dict, Any, List
from functools import reduce
from datetime import datetime

from .models import (
    SeedData, Item, QuizBlueprint, Quiz, Grade,
    Course, Lesson, User, ItemType, Difficulty
)


def load_seed(path: str) -> SeedData:
    """
    Загрузка тестовых данных из JSON файла
    Возвращает иммутабельный кортеж кортежей

    Args:
        path: путь к файлу seed.json

    Returns:
        SeedData: контейнер со всеми данными
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return SeedData.from_dict(data)


def pick_items(items: Tuple[Item, ...], bp: QuizBlueprint) -> Tuple[Item, ...]:
    """
    Фильтрация вопросов по blueprint правилам
    Использует filter и sorted (чистые функции)

    Args:
        items: все доступные вопросы
        bp: blueprint с правилами отбора

    Returns:
        Отобранные вопросы (иммутабельный кортеж)
    """
    rules = bp.rules

    # 1. Фильтр по теме (если указана)
    if topics := rules.get('topics'):
        filtered = filter(lambda i: i.topic in topics, items)
    else:
        filtered = items

    # 2. Фильтр по сложности
    if diff_range := rules.get('difficulty'):
        lo, hi = diff_range
        filtered = filter(lambda i: lo <= i.difficulty.value <= hi, filtered)

    # 3. Фильтр по типу
    if qtypes := rules.get('types'):
        filtered = filter(lambda i: i.type.value in qtypes, filtered)

    # 4. Фильтр по тегам (если указаны)
    if tags := rules.get('tags'):
        filtered = filter(lambda i: any(tag in i.tags for tag in tags), filtered)

    # Преобразуем в список для сортировки
    filtered_list = list(filtered)

    # 5. Сортируем по сложности (опционально)
    if rules.get('sort_by_difficulty', True):
        filtered_list.sort(key=lambda i: i.difficulty.value)

    # 6. Берем нужное количество
    count = rules.get('count', min(10, len(filtered_list)))
    result = filtered_list[:count]

    return tuple(result)


def start_quiz(user_id: str, bp: QuizBlueprint, now: str, pool: Tuple[Item, ...]) -> Quiz:
    """
    Создание нового квиза для пользователя

    Args:
        user_id: ID пользователя
        bp: blueprint квиза
        now: текущее время (строка ISO)
        pool: пул доступных вопросов

    Returns:
        Новый объект Quiz
    """
    # Отбираем вопросы
    selected_items = pick_items(pool, bp)

    # Создаем уникальный ID
    quiz_id = f"quiz_{user_id}_{bp.id}_{now.replace(':', '_').replace('.', '_')}"

    return Quiz(
        id=quiz_id,
        user_id=user_id,
        blueprint_id=bp.id,
        items=selected_items,
        created_at=now,
        status="created"
    )


def sum_score(grades: Tuple[Grade, ...]) -> float:
    """
    Суммирование оценок с использованием reduce

    Args:
        grades: кортеж оценок

    Returns:
        Сумма всех score
    """
    if not grades:
        return 0.0

    # Используем reduce для суммирования
    return reduce(lambda acc, grade: acc + grade.score, grades, 0.0)


def calculate_overview_stats(seed_data: SeedData) -> Dict[str, Any]:
    """
    Агрегация статистики для Overview
    Использует map и reduce для подсчета

    Args:
        seed_data: загруженные данные

    Returns:
        Словарь со статистикой
    """
    items = seed_data.items

    # Подсчет по типам
    type_counts = {}
    for item in items:
        type_name = item.type.value
        type_counts[type_name] = type_counts.get(type_name, 0) + 1

    # Подсчет по сложности
    diff_counts = {}
    for item in items:
        diff = item.difficulty.value
        diff_counts[diff] = diff_counts.get(diff, 0) + 1

    # Распределение по темам
    topic_counts = {}
    for item in items:
        topic = item.topic
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    # Используем map для создания списка сложностей
    difficulties = list(map(lambda i: i.difficulty.value, items))

    # Средняя сложность с использованием reduce
    if difficulties:
        total_diff = reduce(lambda acc, d: acc + d, difficulties, 0)
        avg_difficulty = total_diff / len(difficulties)
    else:
        avg_difficulty = 0

    return {
        "total_courses": len(seed_data.courses),
        "total_lessons": len(seed_data.lessons),
        "total_items": len(items),
        "total_users": len(seed_data.users),
        "total_blueprints": len(seed_data.blueprints),
        "type_distribution": type_counts,
        "difficulty_distribution": diff_counts,
        "topic_distribution": topic_counts,
        "average_difficulty": round(avg_difficulty, 2),
        "unique_tags": len(set(tag for item in items for tag in item.tags))
    }


def filter_by_predicate(items: Tuple[Item, ...], predicate) -> Tuple[Item, ...]:
    """
    Общая функция фильтрации с использованием filter

    Args:
        items: вопросы для фильтрации
        predicate: функция-предикат (Item -> bool)

    Returns:
        Отфильтрованные вопросы
    """
    return tuple(filter(predicate, items))


def map_items_to_ids(items: Tuple[Item, ...]) -> Tuple[str, ...]:
    """
    Преобразование items в их ID с использованием map

    Args:
        items: вопросы

    Returns:
        Кортеж ID вопросов
    """
    return tuple(map(lambda i: i.id, items))