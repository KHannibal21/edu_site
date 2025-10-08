from functools import lru_cache
import random
import time
from typing import Tuple, Optional, List, Dict


@lru_cache(maxsize=128)
def generate_quiz_variant(bp_key: str, pool_idx: Tuple[str, ...], seed: Optional[int] = None) -> Tuple[str, ...]:
    """
    Генерация вариантов заданий с мемоизацией И рекурсией
    """
    if seed is not None:
        random.seed(seed)

    # Парсим ключ blueprint
    try:
        bp_id, topic_mask, diff_bins, _ = bp_key.split(':')
        difficulty_bins = [int(x) for x in diff_bins.split(',')]
        count = int(bp_id.split('')[1]) if '' in bp_id else 10
    except:
        count = 10
        difficulty_bins = [1, 2, 3, 4, 5]

    # Имитация "дорогой" операции
    time.sleep(0.01)  # ← ЗАДЕРЖКА 10ms

    # ПРОДВИНУТАЯ РЕКУРСИЯ: балансировка по сложности
    def recursive_balance_selection(
            remaining_pool: List[str],
            difficulties: List[int],
            target_count: int,
            selected: List[str] = None
    ) -> Tuple[List[str], List[str]]:

        #Рекурсивный алгоритм балансировки заданий по сложностям

        if selected is None:
            selected = []

        # Базовый случай рекурсии - все слоты заполнены или нет сложностей
        if target_count <= 0 or not difficulties:
            return selected, remaining_pool

        # Берем текущую сложность
        current_difficulty = difficulties[0]
        remaining_difficulties = difficulties[1:]

        # Находим задания текущей сложности
        suitable_items = [item for item in remaining_pool if f"diff{current_difficulty}" in item]

        # Вычисляем сколько взять для этой сложности
        slots_for_difficulty = max(1, target_count // (len(difficulties)))

        # Выбираем задания
        chosen = []
        if suitable_items:
            to_take = min(slots_for_difficulty, len(suitable_items))
            chosen = random.sample(suitable_items, to_take)

        # Обновляем пул и выбор
        new_pool = [item for item in remaining_pool if item not in chosen]
        new_selected = selected + chosen
        new_target_count = target_count - len(chosen)

        # РЕКУРСИВНЫЙ ВЫЗОВ для оставшихся сложностей
        return recursive_balance_selection(
            new_pool,
            remaining_difficulties,
            new_target_count,
            new_selected
        )

    # Запускаем рекурсивную балансировку
    pool_list = list(pool_idx)
    balanced_selection, remaining_pool = recursive_balance_selection(
        pool_list, difficulty_bins, count
    )

    # Если остались слоты - заполняем случайными заданиями (старая логика)
    remaining_slots = count - len(balanced_selection)
    if remaining_slots > 0:
        remaining_items = [item for item in remaining_pool if item not in balanced_selection]
        if remaining_items:
            additional = random.sample(remaining_items, min(remaining_slots, len(remaining_items)))
            balanced_selection.extend(additional)

    return tuple(balanced_selection[:count])


def benchmark_generation(iterations: int = 100, pool_size: int = 200) -> dict:
    """
    Замер производительности с настраиваемым размером пула
    """
    bp_key = "bp_10:python,web:1,2,3,4:42"
    pool_idx = tuple(f"item_{i}diff{random.randint(1, 5)}" for i in range(pool_size))

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
        'pool_size': pool_size,
        'uncached_time': round(uncached_time, 3),
        'cached_time': round(cached_time, 3),
        'speedup': round(uncached_time / cached_time, 2) if cached_time > 0 else 0,
        'cache_info': generate_quiz_variant.cache_info()
    }