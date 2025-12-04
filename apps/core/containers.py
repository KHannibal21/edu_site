"""
Лаба №4 - Функциональные паттерны: Maybe/Either
Монадические контейнеры для обработки ошибок
"""
from typing import Generic, TypeVar, Callable, Union, Any
from functools import wraps

T = TypeVar('T')
E = TypeVar('E')
R = TypeVar('R')


class Maybe(Generic[T]):
    """
    Контейнер Maybe (Option) для значений, которые могут отсутствовать
    """

    @staticmethod
    def just(value: T) -> 'Maybe[T]':
        """Создание Maybe с значением"""
        return _Just(value)

    @staticmethod
    def nothing() -> 'Maybe[T]':
        """Создание пустого Maybe"""
        return _Nothing()

    @staticmethod
    def of(value: T) -> 'Maybe[T]':
        """Фабрика: создает Just если значение не None, иначе Nothing"""
        return Maybe.just(value) if value is not None else Maybe.nothing()

    def map(self, f: Callable[[T], R]) -> 'Maybe[R]':
        """Применение функции к значению (если есть)"""
        raise NotImplementedError

    def bind(self, f: Callable[[T], 'Maybe[R]']) -> 'Maybe[R]':
        """Плоское отображение (flatMap)"""
        raise NotImplementedError

    def get_or_else(self, default: T) -> T:
        """Получение значения или значения по умолчанию"""
        raise NotImplementedError

    def is_just(self) -> bool:
        """Проверка, что значение присутствует"""
        raise NotImplementedError

    def is_nothing(self) -> bool:
        """Проверка, что значение отсутствует"""
        raise NotImplementedError

    def to_either(self, error: E) -> 'Either[E, T]':
        """Преобразование Maybe в Either"""
        if self.is_just():
            return Either.right(self.get_or_else(None))
        else:
            return Either.left(error)

    def __str__(self) -> str:
        raise NotImplementedError


class _Just(Maybe[T]):
    """Контейнер с значением"""

    def __init__(self, value: T):
        self._value = value

    def map(self, f: Callable[[T], R]) -> Maybe[R]:
        return Maybe.just(f(self._value))

    def bind(self, f: Callable[[T], Maybe[R]]) -> Maybe[R]:
        return f(self._value)

    def get_or_else(self, default: T) -> T:
        return self._value

    def is_just(self) -> bool:
        return True

    def is_nothing(self) -> bool:
        return False

    def __str__(self) -> str:
        return f"Just({self._value})"


class _Nothing(Maybe[T]):
    """Пустой контейнер"""

    def map(self, f: Callable[[T], R]) -> Maybe[R]:
        return Maybe.nothing()

    def bind(self, f: Callable[[T], Maybe[R]]) -> Maybe[R]:
        return Maybe.nothing()

    def get_or_else(self, default: T) -> T:
        return default

    def is_just(self) -> bool:
        return False

    def is_nothing(self) -> bool:
        return True

    def __str__(self) -> str:
        return "Nothing"


class Either(Generic[E, T]):
    """
    Контейнер Either для операций, которые могут завершиться ошибкой
    Left - ошибка, Right - успешное значение
    """

    @staticmethod
    def left(error: E) -> 'Either[E, T]':
        """Создание Either с ошибкой"""
        return _Left(error)

    @staticmethod
    def right(value: T) -> 'Either[E, T]':
        """Создание Either со значением"""
        return _Right(value)

    @staticmethod
    def of(value: T, error_cls: type = Exception) -> 'Either[Exception, T]':
        """Фабрика: создает Right если нет исключения"""
        return Either.right(value)

    @staticmethod
    def try_except(func: Callable[..., T], *args, **kwargs) -> 'Either[Exception, T]':
        """Выполнение функции с перехватом исключений"""
        try:
            result = func(*args, **kwargs)
            return Either.right(result)
        except Exception as e:
            return Either.left(e)

    def map(self, f: Callable[[T], R]) -> 'Either[E, R]':
        """Применение функции к значению (если Right)"""
        raise NotImplementedError

    def bind(self, f: Callable[[T], 'Either[E, R]']) -> 'Either[E, R]':
        """Плоское отображение (flatMap)"""
        raise NotImplementedError

    def map_left(self, f: Callable[[E], R]) -> 'Either[R, T]':
        """Применение функции к ошибке (если Left)"""
        raise NotImplementedError

    def get_or_else(self, default: T) -> T:
        """Получение значения или значения по умолчанию"""
        raise NotImplementedError

    def is_left(self) -> bool:
        """Проверка, что это Left (ошибка)"""
        raise NotImplementedError

    def is_right(self) -> bool:
        """Проверка, что это Right (успех)"""
        raise NotImplementedError

    def to_maybe(self) -> Maybe[T]:
        """Преобразование Either в Maybe (теряем информацию об ошибке)"""
        if self.is_right():
            return Maybe.just(self.get_or_else(None))
        else:
            return Maybe.nothing()

    def __str__(self) -> str:
        raise NotImplementedError


class _Left(Either[E, T]):
    """Контейнер с ошибкой"""

    def __init__(self, error: E):
        self._error = error

    def map(self, f: Callable[[T], R]) -> Either[E, R]:
        return Either.left(self._error)

    def bind(self, f: Callable[[T], Either[E, R]]) -> Either[E, R]:
        return Either.left(self._error)

    def map_left(self, f: Callable[[E], R]) -> Either[R, T]:
        return Either.left(f(self._error))

    def get_or_else(self, default: T) -> T:
        return default

    def is_left(self) -> bool:
        return True

    def is_right(self) -> bool:
        return False

    def __str__(self) -> str:
        return f"Left({self._error})"


class _Right(Either[E, T]):
    """Контейнер со значением"""

    def __init__(self, value: T):
        self._value = value

    def map(self, f: Callable[[T], R]) -> Either[E, R]:
        return Either.right(f(self._value))

    def bind(self, f: Callable[[T], Either[E, R]]) -> Either[E, R]:
        return f(self._value)

    def map_left(self, f: Callable[[E], R]) -> Either[R, T]:
        return Either.right(self._value)

    def get_or_else(self, default: T) -> T:
        return self._value

    def is_left(self) -> bool:
        return False

    def is_right(self) -> bool:
        return True

    def __str__(self) -> str:
        return f"Right({self._value})"


# Утилитные функции для работы с контейнерами

def maybe_decorator(func: Callable) -> Callable:
    """
    Декоратор для оборачивания функции в Maybe
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return Maybe.of(result)
        except Exception:
            return Maybe.nothing()

    return wrapper


def either_decorator(error_cls: type = Exception):
    """
    Декоратор для оборачивания функции в Either
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return Either.right(result)
            except error_cls as e:
                return Either.left(e)
            except Exception as e:
                # Преобразуем к указанному типу ошибок
                return Either.left(error_cls(str(e)))

        return wrapper

    return decorator


def pipeline(*funcs: Callable) -> Callable:
    """
    Создание пайплайна из функций, возвращающих Maybe/Either
    """

    def composed(arg):
        result = arg
        for func in funcs:
            if isinstance(result, (Maybe, Either)):
                if isinstance(result, Maybe) and result.is_nothing():
                    return result
                if isinstance(result, Either) and result.is_left():
                    return result
                result = result.bind(func)
            else:
                result = func(result)
        return result

    return composed