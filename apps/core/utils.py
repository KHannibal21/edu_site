"""
Вспомогательные утилиты для core модуля
"""
import json
from typing import Any, Dict, List, Tuple
from datetime import datetime


def json_serializer(obj: Any) -> str:
    """Сериализатор для JSON с поддержкой datetime"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def calculate_hash(data: Any) -> str:
    """Вычисление хэша для данных"""
    import hashlib
    data_str = json.dumps(data, sort_keys=True, default=json_serializer)
    return hashlib.md5(data_str.encode()).hexdigest()


def group_by(items: List[Any], key_func) -> Dict[Any, List[Any]]:
    """Группировка элементов по ключу"""
    result = {}
    for item in items:
        key = key_func(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Разбиение списка на чанки"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def timer(func):
    """Декоратор для измерения времени выполнения"""
    import time
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} выполнилась за {end - start:.4f} секунд")
        return result
    return wrapper


def memoize(func):
    """Простой декоратор для мемоизации"""
    cache = {}

    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return wrapper