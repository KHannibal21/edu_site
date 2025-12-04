"""
Интеграционные сервисы для взаимодействия между модулями
"""
from typing import Dict, Any, Tuple
from datetime import datetime

from .models import Item, QuizBlueprint, Quiz, Answer, Rule, User
from .transforms import load_seed, pick_items, start_quiz, sum_score
from .filters import create_complex_filter, apply_filters_chain
from .recursion import flatten_curriculum, walk_blueprint_rules
from .variants import generate_quiz_variant, benchmark_cache_performance
from .containers import Maybe, Either, pipeline
from .validation import safe_item, validate_answer, grade_item
from .lazy import lazy_grade_stream, calculate_top_k
from .events import EventBus, EventType
from .composition import QuizService, GradeService, ReportService, compose, pipe
from .async_ops import generate_variants_batch, grade_submissions_batch


class ApplicationService:
    """
    Основной сервис приложения (интеграция всех модулей)
    """

    def __init__(self, seed_path: str = "data/seed.json"):
        self.seed_path = seed_path
        self.seed_data = None
        self.event_bus = EventBus()
        self._setup_services()
        self._setup_event_handlers()

    def _setup_services(self):
        """Инициализация сервисов"""
        # Сервис квизов
        self.quiz_service = QuizService(
            item_picker=pick_items,
            quiz_generator=start_quiz
        )

        # Сервис оценок
        self.grade_service = GradeService(
            answer_validator=validate_answer,
            item_grader=grade_item,
            grade_creator=lambda quiz, user_id, details, score: {
                "quiz_id": quiz.id,
                "user_id": user_id,
                "score": score,
                "details": details
            }
        )

        # Сервис отчетов
        self.report_service = ReportService(
            aggregators={},
            calculators={}
        )

    def _setup_event_handlers(self):
        """Настройка обработчиков событий"""
        # Состояние для обработчиков
        self.system_state = {
            "active_quizzes": {},
            "user_active_quizzes": {},
            "item_stats": {},
            "topic_stats": {},
            "enrollment_counts": {},
            "active_courses": {},
            "expired_quizzes": []
        }

        # Регистрируем обработчики
        from .events import (
            create_enrollment_handler,
            create_quiz_started_handler,
            create_answered_handler,
            create_graded_handler,
            create_timer_expired_handler,
            create_dashboard_updater
        )

        self.event_bus.subscribe(
            EventType.ENROLLED,
            create_enrollment_handler(self.system_state)
        )

        self.event_bus.subscribe(
            EventType.QUIZ_STARTED,
            create_quiz_started_handler(self.system_state)
        )

        self.event_bus.subscribe(
            EventType.ANSWERED,
            create_answered_handler(self.system_state)
        )

        self.event_bus.subscribe(
            EventType.GRADED,
            create_graded_handler(self.system_state)
        )

        self.event_bus.subscribe(
            EventType.TIMER_EXPIRED,
            create_timer_expired_handler(self.system_state)
        )

        # Дашборд обновляется на все события
        for event_type in EventType:
            self.event_bus.subscribe(
                event_type.value,
                create_dashboard_updater(self.system_state)
            )

    def load_data(self) -> None:
        """Загрузка данных из seed.json"""
        self.seed_data = load_seed(self.seed_path)
        print(f"Данные загружены: {len(self.seed_data.items)} вопросов, "
              f"{len(self.seed_data.users)} пользователей")

    def run_complete_scenario(self, user_id: str, blueprint_id: str) -> Dict[str, Any]:
        """
        Полный сценарий: создание -> прохождение -> оценка -> отчет

        Args:
            user_id: ID пользователя
            blueprint_id: ID черновика

        Returns:
            Результаты сценария
        """
        if not self.seed_data:
            self.load_data()

        # 1. Находим blueprint
        blueprint = next(
            (bp for bp in self.seed_data.blueprints if bp.id == blueprint_id),
            None
        )

        if not blueprint:
            return {"error": "Blueprint not found"}

        # 2. Создаем квиз
        print("Создание квиза...")
        quiz = self.quiz_service.create_quiz(
            user_id,
            blueprint,
            self.seed_data.items,
            datetime.now().isoformat()
        )

        # Публикуем событие
        self.event_bus.publish(EventType.QUIZ_CREATED, {
            "quiz_id": quiz.id,
            "user_id": user_id,
            "blueprint_id": blueprint_id
        })

        # 3. Имитация прохождения квиза
        print("Имитация прохождения квиза...")
        answers = []
        for i, item in enumerate(quiz.items):
            answer = Answer(
                id=f"ans_{quiz.id}_{i}",
                quiz_id=quiz.id,
                item_id=item.id,
                user_id=user_id,
                content={
                    "type": item.type.value,
                    "selected": ["A"] if item.type.value in ["multiple_choice", "single_choice"] else "ответ",
                    "is_correct": i % 2 == 0  # Чередуем правильные/неправильные
                },
                timestamp=datetime.now().isoformat()
            )
            answers.append(answer)

            # Публикуем событие ответа
            self.event_bus.publish(EventType.ANSWERED, {
                "quiz_id": quiz.id,
                "item_id": item.id,
                "is_correct": i % 2 == 0
            })

        # 4. Оценка квиза
        print("Оценка квиза...")
        grade_result = self.grade_service.grade_quiz(
            quiz,
            tuple(answers),
            tuple(self.seed_data.rules),
            blueprint.negative_marking
        )

        # Публикуем событие оценки
        if isinstance(grade_result, dict) and "error" not in grade_result:
            self.event_bus.publish(EventType.GRADED, {
                "quiz_id": quiz.id,
                "user_id": user_id,
                "score": grade_result.get("score", 0),
                "max_score": grade_result.get("max_score", 1),
                "topic": quiz.items[0].topic if quiz.items else "unknown"
            })

        # 5. Генерация отчета
        print("Генерация отчета...")
        report = self.report_service.student_report(
            user_id,
            (grade_result,) if isinstance(grade_result, dict) else (),
            self.seed_data.items
        )

        return {
            "quiz": quiz.id,
            "items_count": len(quiz.items),
            "grade": grade_result,
            "report": report,
            "system_stats": self.system_state.get("dashboard_update", {}),
            "events_processed": self.event_bus.get_event_count()
        }

    def run_performance_test(self) -> Dict[str, Any]:
        """Тестирование производительности всех модулей"""
        if not self.seed_data:
            self.load_data()

        results = {}

        # Тест трансформаций
        print("Тест трансформаций...")
        import time

        start = time.time()
        for _ in range(100):
            pick_items(self.seed_data.items, self.seed_data.blueprints[0])
        results["transforms"] = time.time() - start

        # Тест фильтров
        print("Тест фильтров...")
        start = time.time()
        filter_func = create_complex_filter(
            topic=self.seed_data.items[0].topic,
            difficulty_range=(1, 3)
        )
        for _ in range(100):
            tuple(filter(filter_func, self.seed_data.items))
        results["filters"] = time.time() - start

        # Тест рекурсии
        print("Тест рекурсии...")
        start = time.time()
        for _ in range(50):
            flatten_curriculum(self.seed_data.courses, self.seed_data.lessons)
        results["recursion"] = time.time() - start

        # Тест вариаций (с кэшем)
        print("Тест вариаций с кэшем...")
        bp = self.seed_data.blueprints[0]
        item_indices = tuple(item.to_index() for item in self.seed_data.items[:100])
        pool_hash = hash(item_indices)

        from .variants import create_cache_key
        cache_key = create_cache_key(bp, pool_hash, 42)

        start = time.time()
        for _ in range(100):
            generate_quiz_variant(cache_key, item_indices, 42)
        results["variants_cached"] = time.time() - start

        # Тест ленивых вычислений
        print("Тест ленивых вычислений...")
        start = time.time()
        stream = lazy_grade_stream(
            self.seed_data.items[:50],
            (Answer(
                id=f"test_ans_{i}",
                quiz_id="test_quiz",
                item_id=self.seed_data.items[i % len(self.seed_data.items)].id,
                user_id="test_user",
                content={"is_correct": i % 2 == 0},
                timestamp=datetime.now().isoformat()
            ) for i in range(100)),
            tuple(self.seed_data.rules)
        )
        list(stream)  # Материализация
        results["lazy"] = time.time() - start

        print("\nРезультаты производительности:")
        for module, duration in results.items():
            print(f"  {module}: {duration:.4f} сек")

        return results