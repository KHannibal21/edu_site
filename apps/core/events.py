"""
Лаба №6 - FRP / обработка событий
Шина событий и реактивные пайплайны
"""
from typing import NamedTuple, Callable, Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json


class EventType(str, Enum):
    """Типы событий в системе"""
    ENROLLED = "enrolled"
    QUIZ_CREATED = "quiz_created"
    QUIZ_STARTED = "quiz_started"
    ANSWERED = "answered"
    SUBMITTED = "submitted"
    GRADED = "graded"
    TIMER_EXPIRED = "timer_expired"
    ITEM_VIEWED = "item_viewed"
    COURSE_COMPLETED = "course_completed"


@dataclass(frozen=True)
class Event(NamedTuple):
    """Иммутабельное событие"""
    name: str
    ts: str
    payload: Dict[str, Any]


class EventBus:
    """
    Шина событий с поддержкой подписок
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event, dict], dict]]] = {}
        self._event_history: List[Event] = []
        self._max_history: int = 1000

    def subscribe(
        self,
        event_name: str,
        handler: Callable[[Event, dict], dict],
        priority: int = 0
    ) -> None:
        """
        Подписка на событие

        Args:
            event_name: имя события
            handler: функция-обработчик
            priority: приоритет (чем выше, тем раньше выполнится)
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []

        # Добавляем с учетом приоритета
        self._subscribers[event_name].append((priority, handler))
        self._subscribers[event_name].sort(key=lambda x: x[0], reverse=True)

    def unsubscribe(self, event_name: str, handler: Callable) -> bool:
        """
        Отписка от события

        Args:
            event_name: имя события
            handler: функция для удаления

        Returns:
            True если успешно, иначе False
        """
        if event_name not in self._subscribers:
            return False

        # Ищем и удаляем обработчик
        original_len = len(self._subscribers[event_name])
        self._subscribers[event_name] = [
            (p, h) for p, h in self._subscribers[event_name]
            if h != handler
        ]

        return len(self._subscribers[event_name]) < original_len

    def publish(self, event_name: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Публикация события

        Args:
            event_name: имя события
            payload: данные события

        Returns:
            Список результатов обработчиков
        """
        event = Event(event_name, datetime.now().isoformat(), payload)

        # Сохраняем в историю
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        # Вызываем обработчики
        results = []

        if event_name in self._subscribers:
            for _, handler in self._subscribers[event_name]:
                try:
                    result = handler(event, payload.copy())
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"Error in event handler {handler.__name__}: {e}")

        return results

    def get_recent_events(self, limit: int = 50) -> List[Event]:
        """Получение последних событий"""
        return self._event_history[-limit:] if self._event_history else []

    def get_event_count(self, event_name: Optional[str] = None) -> int:
        """Подсчет событий"""
        if event_name:
            return sum(1 for e in self._event_history if e.name == event_name)
        return len(self._event_history)


# Обработчики событий (чистые функции)

def create_enrollment_handler(state: Dict[str, Any]) -> Callable[[Event, dict], dict]:
    """
    Создание обработчика для события ENROLLED

    Args:
        state: текущее состояние (активные квизы и т.д.)

    Returns:
        Функция-обработчик
    """
    def handler(event: Event, payload: dict) -> dict:
        # Обновляем статистику зачисления
        course_id = payload.get("course_id")
        user_id = payload.get("user_id")

        if course_id and user_id:
            # Добавляем в активные курсы
            if "active_courses" not in state:
                state["active_courses"] = {}

            if course_id not in state["active_courses"]:
                state["active_courses"][course_id] = []

            if user_id not in state["active_courses"][course_id]:
                state["active_courses"][course_id].append(user_id)

            # Обновляем счетчики
            if "enrollment_counts" not in state:
                state["enrollment_counts"] = {}

            state["enrollment_counts"][course_id] = \
                state["enrollment_counts"].get(course_id, 0) + 1

            return {
                "event": event.name,
                "course_id": course_id,
                "user_id": user_id,
                "active_users": len(state["active_courses"][course_id]),
                "total_enrollments": state["enrollment_counts"][course_id],
                "timestamp": event.ts
            }

        return {}

    return handler


def create_quiz_started_handler(state: Dict[str, Any]) -> Callable[[Event, dict], dict]:
    """
    Обработчик для события QUIZ_STARTED
    Обновляет витрину активных квизов
    """
    def handler(event: Event, payload: dict) -> dict:
        quiz_id = payload.get("quiz_id")
        user_id = payload.get("user_id")
        blueprint_id = payload.get("blueprint_id")

        if quiz_id and user_id:
            # Добавляем в активные квизы
            if "active_quizzes" not in state:
                state["active_quizzes"] = {}

            state["active_quizzes"][quiz_id] = {
                "user_id": user_id,
                "blueprint_id": blueprint_id,
                "started_at": event.ts,
                "last_activity": event.ts
            }

            # Обновляем счетчик активных квизов пользователя
            if "user_active_quizzes" not in state:
                state["user_active_quizzes"] = {}

            state["user_active_quizzes"][user_id] = \
                state["user_active_quizzes"].get(user_id, 0) + 1

            return {
                "event": event.name,
                "quiz_id": quiz_id,
                "user_id": user_id,
                "active_quizzes_count": len(state["active_quizzes"]),
                "user_active_count": state["user_active_quizzes"][user_id]
            }

        return {}

    return handler


def create_answered_handler(state: Dict[str, Any]) -> Callable[[Event, dict], dict]:
    """
    Обработчик для события ANSWERED
    Обновляет статистику ответов
    """
    def handler(event: Event, payload: dict) -> dict:
        quiz_id = payload.get("quiz_id")
        item_id = payload.get("item_id")
        is_correct = payload.get("is_correct", False)

        if quiz_id:
            # Обновляем время последней активности
            if "active_quizzes" in state and quiz_id in state["active_quizzes"]:
                state["active_quizzes"][quiz_id]["last_activity"] = event.ts

            # Обновляем статистику по вопросам
            if "item_stats" not in state:
                state["item_stats"] = {}

            if item_id not in state["item_stats"]:
                state["item_stats"][item_id] = {
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "accuracy": 0.0
                }

            stats = state["item_stats"][item_id]
            stats["total_attempts"] += 1

            if is_correct:
                stats["correct_attempts"] += 1

            stats["accuracy"] = stats["correct_attempts"] / stats["total_attempts"]

            return {
                "event": event.name,
                "quiz_id": quiz_id,
                "item_id": item_id,
                "is_correct": is_correct,
                "item_accuracy": stats["accuracy"],
                "total_attempts": stats["total_attempts"]
            }

        return {}

    return handler


def create_graded_handler(state: Dict[str, Any]) -> Callable[[Event, dict], dict]:
    """
    Обработчик для события GRADED
    Обновляет средний балл по теме
    """
    def handler(event: Event, payload: dict) -> dict:
        quiz_id = payload.get("quiz_id")
        user_id = payload.get("user_id")
        score = payload.get("score", 0)
        max_score = payload.get("max_score", 1)
        topic = payload.get("topic")

        if quiz_id and topic:
            # Обновляем статистику по теме
            if "topic_stats" not in state:
                state["topic_stats"] = {}

            if topic not in state["topic_stats"]:
                state["topic_stats"][topic] = {
                    "total_quizzes": 0,
                    "total_score": 0,
                    "total_max_score": 0,
                    "average_score": 0.0
                }

            stats = state["topic_stats"][topic]
            stats["total_quizzes"] += 1
            stats["total_score"] += score
            stats["total_max_score"] += max_score

            if stats["total_max_score"] > 0:
                stats["average_score"] = stats["total_score"] / stats["total_max_score"]

            # Удаляем из активных квизов
            if "active_quizzes" in state and quiz_id in state["active_quizzes"]:
                user_id = state["active_quizzes"][quiz_id]["user_id"]
                del state["active_quizzes"][quiz_id]

                # Обновляем счетчик пользователя
                if "user_active_quizzes" in state and user_id in state["user_active_quizzes"]:
                    state["user_active_quizzes"][user_id] -= 1
                    if state["user_active_quizzes"][user_id] <= 0:
                        del state["user_active_quizzes"][user_id]

            return {
                "event": event.name,
                "quiz_id": quiz_id,
                "topic": topic,
                "score": score,
                "max_score": max_score,
                "percentage": (score / max_score * 100) if max_score > 0 else 0,
                "topic_average": stats["average_score"] * 100,
                "topic_total_quizzes": stats["total_quizzes"]
            }

        return {}

    return handler


def create_timer_expired_handler(state: Dict[str, Any]) -> Callable[[Event, dict], dict]:
    """
    Обработчик для события TIMER_EXPIRED
    Отслеживает просроченные таймеры
    """
    def handler(event: Event, payload: dict) -> dict:
        quiz_id = payload.get("quiz_id")
        user_id = payload.get("user_id")

        if quiz_id:
            # Помечаем как просроченный
            if "expired_quizzes" not in state:
                state["expired_quizzes"] = []

            if quiz_id not in state["expired_quizzes"]:
                state["expired_quizzes"].append(quiz_id)

            # Удаляем из активных
            if "active_quizzes" in state and quiz_id in state["active_quizzes"]:
                del state["active_quizzes"][quiz_id]

            return {
                "event": event.name,
                "quiz_id": quiz_id,
                "user_id": user_id,
                "total_expired": len(state["expired_quizzes"]),
                "timestamp": event.ts
            }

        return {}

    return handler


def create_dashboard_updater(state: Dict[str, Any]) -> Callable[[Event, dict], dict]:
    """
    Композитный обработчик для обновления всех дашбордов
    """
    def handler(event: Event, payload: dict) -> dict:
        # Вычисляем общую статистику
        active_quizzes = len(state.get("active_quizzes", {}))
        expired_quizzes = len(state.get("expired_quizzes", []))
        total_enrollments = sum(state.get("enrollment_counts", {}).values())
        active_courses = len(state.get("active_courses", {}))

        # Вычисляем среднюю точность по всем вопросам
        item_stats = state.get("item_stats", {})
        if item_stats:
            total_accuracy = sum(stats["accuracy"] for stats in item_stats.values())
            avg_accuracy = total_accuracy / len(item_stats)
        else:
            avg_accuracy = 0

        # Самые сложные темы (по среднему баллу)
        topic_stats = state.get("topic_stats", {})
        difficult_topics = []

        if topic_stats:
            difficult_topics = sorted(
                [(topic, stats["average_score"]) for topic, stats in topic_stats.items()],
                key=lambda x: x[1]
            )[:3]  # Топ-3 самых сложных

        return {
            "dashboard_update": {
                "timestamp": event.ts,
                "active_quizzes": active_quizzes,
                "expired_quizzes": expired_quizzes,
                "total_enrollments": total_enrollments,
                "active_courses": active_courses,
                "average_accuracy": round(avg_accuracy * 100, 1),
                "difficult_topics": difficult_topics,
                "recent_event": event.name
            }
        }

    return handler