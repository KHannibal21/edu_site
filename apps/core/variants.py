"""
Лаба №3 - Продвинутая рекурсия + мемоизация
Генерация вариантов квизов с кэшированием
"""
import random
import time
import hashlib
import json
from functools import lru_cache
from typing import Tuple, Dict, Any, List, Optional
from datetime import datetime

from .models import Item, QuizBlueprint, ItemType, Difficulty
from .filters import create_complex_filter
from .transforms import pick_items


def create_cache_key(
        bp: QuizBlueprint,
        pool_hash: int,
        seed: Optional[int] = None
) -> str:
    """
    Создание иммутабельного ключа для кэша

    Args:
        bp: blueprint квиза
        pool_hash: хэш пула вопросов
        seed: случайное зерно (опционально)

    Returns:
        Строковый ключ для кэширования
    """
    # Сериализуем правила для создания стабильного ключа
    rules_str = json.dumps(bp.rules, sort_keys=True)

    key_parts = [
        bp.id,
        str(pool_hash),
        rules_str,
        str(bp.time_limit_minutes),
        str(bp.shuffle_questions),
        str(bp.shuffle_answers)
    ]

    if seed is not None:
        key_parts.append(str(seed))

    # Хэшируем для компактности
    key_string = "_".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


@lru_cache(maxsize=128)
def generate_quiz_variant(
        cache_key: str,
        item_indices: Tuple[int, ...],
        seed: Optional[int] = None
) -> Tuple[str, ...]:
    """
    Генерация варианта квиза с кэшированием

    Args:
        cache_key: ключ кэша (должен быть иммутабельным)
        item_indices: кортеж индексов вопросов (для восстановления)
        seed: случайное зерно

    Returns:
        Кортеж ID вопросов в варианте
    """
    # Восстанавливаем вопросы из индексов (в реальности нужен доступ к хранилищу)
    # Здесь для простоты возвращаем индексы как строки

    if seed is not None:
        random.seed(seed)

    # Преобразуем индексы в список для перемешивания
    indices_list = list(item_indices)

    # Балансировка по сложности
    # (упрощенная реализация - в реальности более сложная логика)
    if len(indices_list) > 5:
        # Делим на группы по сложности
        easy = indices_list[:len(indices_list) // 3]
        medium = indices_list[len(indices_list) // 3:2 * len(indices_list) // 3]
        hard = indices_list[2 * len(indices_list) // 3:]

        # Выбираем пропорционально
        result = []
        result.extend(random.sample(easy, min(3, len(easy))))
        result.extend(random.sample(medium, min(4, len(medium))))
        result.extend(random.sample(hard, min(3, len(hard))))

        # Перемешиваем
        random.shuffle(result)
    else:
        # Если вопросов мало, берем все
        result = indices_list

    # Преобразуем в строки (ID вопросов)
    return tuple(str(idx) for idx in result[:10])  # Ограничиваем 10 вопросами


def generate_variant_with_balance(
        bp: QuizBlueprint,
        items: Tuple[Item, ...],
        seed: Optional[int] = None
) -> Tuple[Item, ...]:
    """
    Генерация сбалансированного варианта
    (без кэширования, для сравнения производительности)

    Args:
        bp: blueprint
        items: доступные вопросы
        seed: случайное зерно

    Returns:
        Кортеж отобранных вопросов
    """
    start_time = time.time()

    if seed is not None:
        random.seed(seed)

    # Фильтрация по правилам blueprint
    filtered_items = pick_items(items, bp)

    if not filtered_items:
        return tuple()

    # Балансировка по темам (если указаны темы в правилах)
    if 'topics' in bp.rules:
        topics = bp.rules['topics']
        items_by_topic = {}

        for topic in topics:
            topic_items = [item for item in filtered_items if item.topic == topic]
            if topic_items:
                items_by_topic[topic] = topic_items

        # Пропорциональный отбор из каждой темы
        result = []
        items_per_topic = max(1, bp.rules.get('count', 10) // len(topics))

        for topic, topic_items in items_by_topic.items():
            if len(topic_items) > items_per_topic:
                result.extend(random.sample(topic_items, items_per_topic))
            else:
                result.extend(topic_items)
    else:
        # Случайный отбор
        count = min(bp.rules.get('count', 10), len(filtered_items))
        result = random.sample(list(filtered_items), count)

    # Балансировка по сложности
    result.sort(key=lambda x: x.difficulty.value)

    end_time = time.time()

    # Для демонстрации производительности
    print(f"Generation time (uncached): {end_time - start_time:.4f} seconds")

    return tuple(result)


def benchmark_cache_performance(
        bp: QuizBlueprint,
        items: Tuple[Item, ...],
        iterations: int = 100
) -> Dict[str, float]:
    """
    Замер производительности до/после кэширования

    Args:
        bp: blueprint для тестирования
        items: пул вопросов
        iterations: количество итераций

    Returns:
        Словарь с результатами бенчмарка
    """
    # Подготовка данных для кэшированной функции
    item_indices = tuple(item.to_index() for item in items)
    pool_hash = hash(item_indices)
    cache_key = create_cache_key(bp, pool_hash, 42)

    # Тест без кэширования
    uncached_times = []
    for i in range(iterations):
        start = time.time()
        generate_variant_with_balance(bp, items, seed=i)
        uncached_times.append(time.time() - start)

    # Тест с кэшированием (первый вызов и повторные)
    cached_times = []

    # Первый вызов (кэш пустой)
    start = time.time()
    result1 = generate_quiz_variant(cache_key, item_indices, 42)
    cached_times.append(time.time() - start)

    # Повторные вызовы (должны быть быстрее)
    for i in range(1, iterations):
        start = time.time()
        result2 = generate_quiz_variant(cache_key, item_indices, 42)
        cached_times.append(time.time() - start)

        # Проверка, что результаты одинаковые (кэш работает)
        if result1 != result2:
            print(f"Warning: cache inconsistency at iteration {i}")

    avg_uncached = sum(uncached_times) / len(uncached_times)
    avg_cached = sum(cached_times) / len(cached_times)

    return {
        "iterations": iterations,
        "avg_uncached_ms": avg_uncached * 1000,
        "avg_cached_ms": avg_cached * 1000,
        "speedup": avg_uncached / avg_cached if avg_cached > 0 else 0,
        "cache_hits": iterations - 1,  # после первого вызова
        "cache_misses": 1
    }


def batch_generate_variants(
        blueprints: Tuple[QuizBlueprint, ...],
        items: Tuple[Item, ...],
        seed: Optional[int] = None
) -> Dict[str, Tuple[str, ...]]:
    """
    Пакетная генерация вариантов для нескольких blueprints

    Args:
        blueprints: кортеж blueprints
        items: пул вопросов
        seed: базовое зерно

    Returns:
        Словарь {blueprint_id: вариант}
    """
    results = {}
    item_indices = tuple(item.to_index() for item in items)

    for i, bp in enumerate(blueprints):
        # Уникальное зерно для каждого blueprint
        current_seed = seed + i if seed is not None else None
        pool_hash = hash(item_indices)
        cache_key = create_cache_key(bp, pool_hash, current_seed)

        variant = generate_quiz_variant(cache_key, item_indices, current_seed)
        results[bp.id] = variant

    return results