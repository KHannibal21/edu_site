from typing import TypeVar, Generic, Callable, Any
from functools import wraps

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')


# Maybe Monad
class Maybe(Generic[T]):
    """Maybe monad для обработки nullable значений"""

    def __init__(self, value: T | None):
        self._value = value

    def map(self, func: Callable[[T], U]) -> 'Maybe[U]':
        """Применяет функцию к значению, если оно существует"""
        if self._value is None:
            return Maybe(None)
        return Maybe(func(self._value))

    def bind(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        """Позволяет композицию Maybe-функций"""
        if self._value is None:
            return Maybe(None)
        return func(self._value)

    def get_or_else(self, default: T) -> T:
        """Возвращает значение или default"""
        return self._value if self._value is not None else default

    def is_just(self) -> bool:
        return self._value is not None

    def is_nothing(self) -> bool:
        return self._value is None

    def __repr__(self):
        return f"Just({self._value})" if self._value is not None else "Nothing"


# Either Monad
class Either(Generic[E, T]):
    """Either monad для обработки операций с возможной ошибкой"""

    def __init__(self, value: T = None, error: E = None):
        self._value = value
        self._error = error

    @classmethod
    def right(cls, value: T) -> 'Either[E, T]':
        """Создает успешный Either"""
        return cls(value=value, error=None)

    @classmethod
    def left(cls, error: E) -> 'Either[E, T]':
        """Создает Either с ошибкой"""
        return cls(value=None, error=error)

    def map(self, func: Callable[[T], U]) -> 'Either[E, U]':
        """Применяет функцию к успешному значению"""
        if self._error is not None:
            return Either.left(self._error)
        return Either.right(func(self._value))

    def bind(self, func: Callable[[T], 'Either[E, U]']) -> 'Either[E, U]':
        """Позволяет композицию Either-функций"""
        if self._error is not None:
            return Either.left(self._error)
        return func(self._value)

    def get_or_else(self, default: T) -> T:
        """Возвращает значение или default при ошибке"""
        return self._value if self._error is None else default

    def is_right(self) -> bool:
        return self._error is None

    def is_left(self) -> bool:
        return self._error is not None

    def __repr__(self):
        if self._error is not None:
            return f"Left({self._error})"
        return f"Right({self._value})"


# Декораторы для удобства
def maybe_result(func: Callable) -> Callable:
    """Декоратор для автоматического оборачивания в Maybe"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return Maybe(result)
        except Exception:
            return Maybe(None)

    return wrapper


def either_result(error_type: type = dict) -> Callable:
    """Декоратор для автоматического оборачивания в Either"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return Either.right(result)
            except Exception as e:
                return Either.left(error_type({"error": str(e)}))

        return wrapper

    return decorator