from functools import lru_cache
import random
import time
from typing import Tuple, Optional


@lru_cache(maxsize=128)
def generate_quiz_variant(bp_key: str, pool_idx: Tuple[str, ...], seed: Optional[int] = None) -> Tuple[str, ...]:
    """
    Генерация вариантов квиза с мемоизацией
    """
    if seed is not None:
        random.seed(seed)

    # Парсим ключ blueprint
    try:
        bp_id, topic_mask, diff_bins, _ = bp_key.split(':')
        difficulty_bins = [int(x) for x in diff_bins.split(',')]
        count = int(bp_id.split('_')[1]) if '_' in bp_id else 10
    except:
        count = 10
        difficulty_bins = [1, 2, 3, 4, 5]

    # Имитация "дорогой" операции
    time.sleep(0.01)  # ← ЗАДЕРЖКА 10ms

    # Балансировка по сложности
    selected_items = []
    remaining_slots = count

    for difficulty in difficulty_bins:
        if remaining_slots <= 0:
            break

        # Фильтруем задания текущей сложности
        difficulty_items = [item_id for item_id in pool_idx
                            if f"diff_{difficulty}" in item_id]

        if difficulty_items:
            slots_for_difficulty = max(1, remaining_slots // len(difficulty_bins))
            selected = random.sample(difficulty_items,
                                     min(slots_for_difficulty, len(difficulty_items)))
            selected_items.extend(selected)
            remaining_slots -= len(selected)

    # Заполняем оставшиеся слоты
    if remaining_slots > 0:
        remaining_items = [item_id for item_id in pool_idx
                           if item_id not in selected_items]
        if remaining_items:
            additional = random.sample(remaining_items,
                                       min(remaining_slots, len(remaining_items)))
            selected_items.extend(additional)

    return tuple(selected_items[:count])


def benchmark_generation(iterations: int = 100) -> dict:
    """
    Замер производительности до/после кэша
    """
    # Подготавливаем тестовые данные
    bp_key = "bp_10:python,web:1,2,3,4:42"
    pool_idx = tuple(f"item_{i}_diff_{random.randint(1, 5)}" for i in range(200))

    # Замер БЕЗ кэша
    start_time = time.time()
    for i in range(iterations):
        generate_quiz_variant.cache_clear()
        generate_quiz_variant(bp_key, pool_idx, i)
    uncached_time = time.time() - start_time

    # Замер С кэшем
    start_time = time.time()
    for i in range(iterations):
        generate_quiz_variant(bp_key, pool_idx, 42)
    cached_time = time.time() - start_time

    return {
        'iterations': iterations,
        'uncached_time': round(uncached_time, 3),
        'cached_time': round(cached_time, 3),
        'speedup': round(uncached_time / cached_time, 2) if cached_time > 0 else 0,
        'cache_info': generate_quiz_variant.cache_info()
    }