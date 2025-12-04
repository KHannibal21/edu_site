"""
Лаба №7 - Композиция/модульность + интеграция с ООП
Утилиты композиции и сервисные фасады
"""
from typing import Callable, Any, List, Dict, Tuple, Optional
from functools import reduce

from .models import Item, QuizBlueprint, Quiz, Answer, Grade, Rule, User
from .transforms import pick_items, start_quiz
from .validation import process_attempt_pipeline, create_grade_from_results


def compose(*funcs: Callable) -> Callable:
    """
    Композиция функций: f(g(x)) = compose(f, g)(x)

    Args:
        *funcs: функции для композиции (справа налево)

    Returns:
        Составная функция
    """
    def composed(arg):
        result = arg
        for f in reversed(funcs):
            result = f(result)
        return result
    return composed


def pipe(*funcs: Callable) -> Callable:
    """
    Конвейер функций: f(g(x)) = pipe(g, f)(x)

    Args:
        *funcs: функции для конвейера (слева направо)

    Returns:
        Конвейерная функция
    """
    def piped(arg):
        result = arg
        for f in funcs:
            result = f(result)
        return result
    return piped


def identity(x: Any) -> Any:
    """Функция-тождество"""
    return x


def tap(f: Callable) -> Callable:
    """
    Функция для побочных эффектов (логирование и т.д.)
    Возвращает исходный аргумент
    """
    def tapped(arg):
        f(arg)
        return arg
    return tapped


class QuizService:
    """
    Сервис для работы с квизами (фасад из чистых функций)
    """

    def __init__(
        self,
        item_picker: Callable[[Tuple[Item, ...], QuizBlueprint], Tuple[Item, ...]],
        quiz_generator: Callable[[str, QuizBlueprint, str, Tuple[Item, ...]], Quiz],
        rule_applier: Optional[Callable[[QuizBlueprint], Dict[str, Any]]] = None
    ):
        self.item_picker = item_picker
        self.quiz_generator = quiz_generator
        self.rule_applier = rule_applier or (lambda bp: bp.rules)

    def create_quiz(
        self,
        user_id: str,
        blueprint: QuizBlueprint,
        item_pool: Tuple[Item, ...],
        timestamp: str = None
    ) -> Quiz:
        """
        Создание квиза через композицию функций

        Args:
            user_id: ID пользователя
            blueprint: шаблон квиза
            item_pool: пул вопросов
            timestamp: время создания

        Returns:
            Созданный квиз
        """
        from datetime import datetime

        if timestamp is None:
            timestamp = datetime.now().isoformat()

        # Композиция: pick_items -> start_quiz
        create_pipeline = compose(
            lambda items: self.quiz_generator(user_id, blueprint, timestamp, items),
            lambda items: self.item_picker(items, blueprint)
        )

        return create_pipeline(item_pool)

    def create_personalized_quiz(
        self,
        user: User,
        blueprint: QuizBlueprint,
        item_pool: Tuple[Item, ...],
        user_history: Dict[str, Any]
    ) -> Quiz:
        """
        Создание персонализированного квиза на основе истории пользователя

        Args:
            user: пользователь
            blueprint: шаблон
            item_pool: пул вопросов
            user_history: история ответов пользователя

        Returns:
            Персонализированный квиз
        """
        from datetime import datetime

        # Фильтрация вопросов, которые пользователь уже видел
        seen_items = user_history.get("seen_items", [])
        unseen_items = [item for item in item_pool if item.id not in seen_items]

        # Если мало непросмотренных вопросов, используем все
        if len(unseen_items) < blueprint.rules.get("count", 10) // 2:
            filtered_pool = item_pool
        else:
            filtered_pool = tuple(unseen_items)

        # Создание квиза
        quiz = self.create_quiz(
            user.id,
            blueprint,
            filtered_pool,
            datetime.now().isoformat()
        )

        return quiz

    def batch_create_quizzes(
        self,
        user_ids: List[str],
        blueprint: QuizBlueprint,
        item_pool: Tuple[Item, ...]
    ) -> List[Quiz]:
        """
        Пакетное создание квизов

        Args:
            user_ids: список ID пользователей
            blueprint: шаблон
            item_pool: пул вопросов

        Returns:
            Список созданных квизов
        """
        from datetime import datetime
        timestamp = datetime.now().isoformat()

        # Используем map для создания квизов
        return [
            self.create_quiz(user_id, blueprint, item_pool, timestamp)
            for user_id in user_ids
        ]


class GradeService:
    """
    Сервис для оценки квизов (фасад из чистых функций)
    """

    def __init__(
        self,
        answer_validator: Callable[[Item, Answer, Tuple[Rule, ...]], Any],
        item_grader: Callable[[Item, Answer, Tuple[Rule, ...], bool], Any],
        grade_creator: Callable[[Quiz, str, Dict[str, float], float], Any]
    ):
        self.answer_validator = answer_validator
        self.item_grader = item_grader
        self.grade_creator = grade_creator

    def grade_quiz(
        self,
        quiz: Quiz,
        answers: Tuple[Answer, ...],
        rules: Tuple[Rule, ...],
        negative_marking: bool = False
    ) -> Any:  # В реальности должен возвращать Grade
        """
        Оценка квиза через композицию валидации и оценки

        Args:
            quiz: квиз для оценки
            answers: ответы пользователя
            rules: правила оценки
            negative_marking: учитывать ли штрафы

        Returns:
            Результат оценки (Grade или ошибка)
        """
        from .containers import Either

        # Пайплайн обработки попытки
        result = process_attempt_pipeline(
            quiz.items,
            answers,
            rules,
            negative_marking
        )

        # Преобразование результата в Grade
        if result.is_right():
            details, total_score = result.get_or_else(({}, 0))

            grade_result = self.grade_creator(
                quiz,
                quiz.user_id,
                details,
                total_score
            )

            return grade_result
        else:
            return result

    def calculate_item_difficulty(
        self,
        items: Tuple[Item, ...],
        answer_history: Dict[str, List[bool]]
    ) -> Dict[str, float]:
        """
        Вычисление дискриминативности вопросов

        Args:
            items: вопросы
            answer_history: история ответов {item_id: [correct_bool]}

        Returns:
            Словарь с дискриминативностью вопросов
        """
        difficulty_scores = {}

        for item in items:
            attempts = answer_history.get(item.id, [])

            if attempts:
                correct_rate = sum(attempts) / len(attempts)
                # Преобразуем в сложность 1-5
                difficulty = 1 + (1 - correct_rate) * 4  # 0% -> 5, 100% -> 1
                difficulty_scores[item.id] = round(difficulty, 2)
            else:
                difficulty_scores[item.id] = 3.0  # Средняя сложность по умолчанию

        return difficulty_scores


class ReportService:
    """
    Сервис для генерации отчетов (фасад из чистых функций)
    """

    def __init__(
        self,
        aggregators: Dict[str, Callable],
        calculators: Dict[str, Callable]
    ):
        self.aggregators = aggregators
        self.calculators = calculators

    def course_report(
        self,
        course_id: str,
        items: Tuple[Item, ...],
        grades: Tuple[Any, ...],  # В реальности Tuple[Grade, ...]
        answer_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Генерация отчета по курсу

        Args:
            course_id: ID курса
            items: вопросы курса
            grades: оценки по курсу
            answer_history: история ответов

        Returns:
            Отчет по курсу
        """
        # Фильтруем вопросы курса
        course_items = [item for item in items if any(
            course_id in getattr(item, 'course_id', '') or
            course_id in getattr(item, 'lesson_id', '')
            for attr in ['course_id', 'lesson_id']
            if hasattr(item, attr)
        )]

        if not course_items:
            return {"error": "No items found for course"}

        # Вычисляем среднюю сложность
        avg_difficulty = sum(item.difficulty.value for item in course_items) / len(course_items)

        # Вычисляем дискриминативность
        if "discrimination" in self.calculators:
            discrimination = self.calculators["discrimination"](course_items, answer_history)
        else:
            discrimination = {}

        # Вычисляем средний балл
        if grades:
            total_score = sum(getattr(g, 'score', 0) for g in grades)
            total_max = sum(getattr(g, 'max_score', 1) for g in grades)
            avg_score = total_score / total_max if total_max > 0 else 0
        else:
            avg_score = 0

        # Распределение по типам вопросов
        type_distribution = {}
        for item in course_items:
            type_name = item.type.value
            type_distribution[type_name] = type_distribution.get(type_name, 0) + 1

        # Топ-5 самых сложных вопросов
        difficulty_scores = {}
        for item in course_items:
            attempts = answer_history.get(item.id, [])
            if attempts:
                correct_rate = sum(attempts) / len(attempts)
                difficulty_scores[item.id] = correct_rate

        hardest_items = sorted(
            difficulty_scores.items(),
            key=lambda x: x[1]
        )[:5] if difficulty_scores else []

        return {
            "course_id": course_id,
            "total_items": len(course_items),
            "average_difficulty": round(avg_difficulty, 2),
            "average_score": round(avg_score * 100, 1),
            "type_distribution": type_distribution,
            "hardest_items": hardest_items,
            "discrimination_scores": discrimination,
            "completion_rate": self._calculate_completion_rate(grades, len(course_items))
        }

    def student_report(
        self,
        user_id: str,
        grades: Tuple[Any, ...],  # Tuple[Grade, ...]
        items: Tuple[Item, ...]
    ) -> Dict[str, Any]:
        """
        Отчет по студенту

        Args:
            user_id: ID студента
            grades: оценки студента
            items: все вопросы

        Returns:
            Отчет по студенту
        """
        # Фильтруем оценки студента
        student_grades = [g for g in grades if getattr(g, 'user_id', '') == user_id]

        if not student_grades:
            return {"error": "No grades found for student"}

        # Вычисляем статистику
        total_quizzes = len(student_grades)
        avg_score = sum(getattr(g, 'score', 0) for g in student_grades) / total_quizzes
        avg_percentage = sum(
            (getattr(g, 'score', 0) / getattr(g, 'max_score', 1) * 100)
            for g in student_grades
        ) / total_quizzes

        # Прогресс по темам
        topic_progress = {}
        for grade in student_grades:
            # Здесь нужно получить тему квиза из самого grade или через quiz
            # Упрощенная реализация
            topic = getattr(grade, 'topic', 'unknown')
            if topic not in topic_progress:
                topic_progress[topic] = []

            score = getattr(grade, 'score', 0)
            max_score = getattr(grade, 'max_score', 1)
            topic_progress[topic].append(score / max_score if max_score > 0 else 0)

        # Усредняем по темам
        topic_avg = {
            topic: sum(scores) / len(scores)
            for topic, scores in topic_progress.items()
        }

        # Сильные и слабые стороны
        strong_topics = [
            topic for topic, avg in topic_avg.items()
            if avg >= 0.7
        ]

        weak_topics = [
            topic for topic, avg in topic_avg.items()
            if avg < 0.5
        ]

        return {
            "user_id": user_id,
            "total_quizzes": total_quizzes,
            "average_score": round(avg_score, 2),
            "average_percentage": round(avg_percentage, 1),
            "topic_progress": topic_avg,
            "strong_topics": strong_topics,
            "weak_topics": weak_topics,
            "improvement_suggestions": self._generate_suggestions(weak_topics, items)
        }

    def _calculate_completion_rate(
        self,
        grades: Tuple[Any, ...],
        total_items: int
    ) -> float:
        """Вычисление процента завершения"""
        if not grades or total_items == 0:
            return 0.0

        # Упрощенный расчет
        completed_items = sum(
            len(getattr(g, 'details', {}))
            for g in grades
        )

        return min(100.0, (completed_items / (len(grades) * total_items)) * 100)

    def _generate_suggestions(
        self,
        weak_topics: List[str],
        items: Tuple[Item, ...]
    ) -> List[str]:
        """Генерация рекомендаций для улучшения"""
        suggestions = []

        for topic in weak_topics:
            topic_items = [item for item in items if item.topic == topic]

            if topic_items:
                # Рекомендуем практиковать конкретные типы вопросов
                item_types = set(item.type.value for item in topic_items)
                suggestions.append(
                    f"Практикуйте тему '{topic}' с типами вопросов: {', '.join(item_types)}"
                )

        return suggestions