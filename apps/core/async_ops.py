"""
Лаба №8 - Параллелизм/асинхронность + финальная интеграция
Асинхронные операции и end-to-end пайплайны
"""
import asyncio
import time
from typing import List, Dict, Tuple, Any, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime

from .models import QuizBlueprint, Item, Quiz, Answer, Grade
from .variants import generate_quiz_variant, create_cache_key
from .validation import process_attempt_pipeline
from .composition import QuizService, GradeService, ReportService


async def generate_variants_batch(
    blueprints: List[QuizBlueprint],
    pool: List[Item],
    seed: Optional[int] = None
) -> Dict[str, Tuple[str, ...]]:
    """
    Асинхронная пакетная генерация вариантов

    Args:
        blueprints: список blueprints
        pool: пул вопросов
        seed: базовое зерно

    Returns:
        Словарь {blueprint_id: вариант}
    """
    # Преобразуем вопросы в индексы для кэширования
    item_indices = tuple(item.to_index() for item in pool)
    pool_hash = hash(item_indices)

    async def generate_for_bp(bp: QuizBlueprint, idx: int) -> Tuple[str, Tuple[str, ...]]:
        """Генерация варианта для одного blueprint"""
        current_seed = seed + idx if seed is not None else None
        cache_key = create_cache_key(bp, pool_hash, current_seed)

        # Используем синхронную функцию в отдельном потоке
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            variant = await loop.run_in_executor(
                executor,
                generate_quiz_variant,
                cache_key,
                item_indices,
                current_seed
            )

        return bp.id, variant

    # Создаем задачи для всех blueprints
    tasks = [
        generate_for_bp(bp, i)
        for i, bp in enumerate(blueprints)
    ]

    # Выполняем параллельно
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Обрабатываем результаты
    variants = {}
    for result in results:
        if isinstance(result, Exception):
            print(f"Error generating variant: {result}")
            continue

        bp_id, variant = result
        variants[bp_id] = variant

    return variants


async def grade_submissions_batch(
    quizzes: List[Quiz],
    answers_list: List[List[Answer]],
    rules: Tuple[Any, ...],  # В реальности Tuple[Rule, ...]
    negative_marking: bool = False
) -> Dict[str, Any]:  # В реальности Dict[str, Grade]
    """
    Асинхронная пакетная оценка квизов

    Args:
        quizzes: список квизов
        answers_list: список списков ответов (соответствует quizzes)
        rules: правила оценки
        negative_marking: учитывать ли штрафы

    Returns:
        Словарь с оценками {quiz_id: Grade}
    """
    async def grade_single(
        quiz: Quiz,
        answers: List[Answer]
    ) -> Tuple[str, Any]:
        """Оценка одного квиза"""
        try:
            # Используем синхронную функцию в отдельном потоке
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    process_attempt_pipeline,
                    quiz.items,
                    tuple(answers),
                    rules,
                    negative_marking
                )

            if hasattr(result, 'is_right') and result.is_right():
                details, total_score = result.get_or_else(({}, 0))

                # Создаем объект Grade
                grade = {
                    "grade_id": f"grade_{quiz.id}_{datetime.now().isoformat()}",
                    "quiz_id": quiz.id,
                    "user_id": quiz.user_id,
                    "score": total_score,
                    "max_score": len(quiz.items),
                    "details": details,
                    "created_at": datetime.now().isoformat()
                }

                return quiz.id, grade
            else:
                return quiz.id, {"error": "Grading failed"}

        except Exception as e:
            return quiz.id, {"error": str(e)}

    # Создаем задачи для всех квизов
    tasks = [
        grade_single(quiz, answers)
        for quiz, answers in zip(quizzes, answers_list)
        if answers  # Только квизы с ответами
    ]

    # Выполняем параллельно
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Обрабатываем результаты
    grades = {}
    for result in results:
        if isinstance(result, Exception):
            print(f"Error grading submission: {result}")
            continue

        quiz_id, grade = result
        grades[quiz_id] = grade

    return grades


async def end_to_end_pipeline(
    blueprints: List[QuizBlueprint],
    items: List[Item],
    users: List[str],
    rules: Tuple[Any, ...]
) -> Dict[str, Any]:
    """
    End-to-end пайплайн: генерация -> выполнение -> оценка -> отчет

    Args:
        blueprints: шаблоны квизов
        items: пул вопросов
        users: список пользователей
        rules: правила оценки

    Returns:
        Полный отчет
    """
    start_time = time.time()

    print("1. Генерация вариантов квизов...")
    variants = await generate_variants_batch(blueprints, items, seed=42)

    print(f"2. Создание квизов для {len(users)} пользователей...")
    # Создаем квизы на основе сгенерированных вариантов
    quizzes = []
    for user_id in users[:10]:  # Ограничимся 10 пользователями для примера
        for bp in blueprints:
            if bp.id in variants:
                # Создаем квиз с выбранными вопросами
                # В реальности нужно восстановить вопросы по ID из variants[bp.id]
                quiz = Quiz(
                    id=f"quiz_{user_id}_{bp.id}_{datetime.now().isoformat()}",
                    user_id=user_id,
                    blueprint_id=bp.id,
                    items=tuple(items[:10]),  # Упрощенно: берем первые 10 вопросов
                    created_at=datetime.now().isoformat(),
                    status="created"
                )
                quizzes.append(quiz)

    print(f"3. Генерация ответов для {len(quizzes)} квизов...")
    # Генерируем тестовые ответы
    answers_by_quiz = {}
    for quiz in quizzes:
        answers = []
        for i, item in enumerate(quiz.items[:5]):  # Ответы на первые 5 вопросов
            answer = {
                "id": f"ans_{quiz.id}_{i}",
                "quiz_id": quiz.id,
                "item_id": item.id,
                "user_id": quiz.user_id,
                "content": {
                    "type": item.type.value,
                    "selected": ["A"] if item.type.value == "multiple_choice" else "answer",
                    "is_correct": i % 2 == 0  # Чередуем правильные/неправильные
                },
                "timestamp": datetime.now().isoformat()
            }
            answers.append(answer)
        answers_by_quiz[quiz.id] = answers

    print("4. Пакетная оценка квизов...")
    grades = await grade_submissions_batch(
        quizzes,
        [answers_by_quiz.get(quiz.id, []) for quiz in quizzes],
        rules,
        negative_marking=False
    )

    print("5. Генерация отчетов...")
    # Создаем сервис отчетов
    report_service = ReportService({}, {})

    # Отчет по курсам (упрощенно)
    course_reports = {}
    for bp in blueprints:
        course_id = bp.course_id if hasattr(bp, 'course_id') else "default"

        # Фильтруем оценки для этого курса
        course_grades = [
            grade for quiz_id, grade in grades.items()
            if any(bp.id in quiz_id for bp in blueprints if bp.course_id == course_id)
        ]

        # Генерируем отчет
        report = report_service.course_report(
            course_id,
            tuple(items),
            tuple(course_grades),
            {}  # Пустая история для примера
        )
        course_reports[course_id] = report

    end_time = time.time()

    return {
        "execution_time": round(end_time - start_time, 2),
        "total_blueprints": len(blueprints),
        "total_quizzes": len(quizzes),
        "total_grades": len(grades),
        "success_rate": len([g for g in grades.values() if "error" not in g]) / len(grades) * 100,
        "course_reports": course_reports,
        "performance_metrics": {
            "variants_per_second": len(variants) / (end_time - start_time) * 0.2,
            "quizzes_per_second": len(quizzes) / (end_time - start_time) * 0.4,
            "grades_per_second": len(grades) / (end_time - start_time) * 0.4
        }
    }


async def parallel_data_processing(
    data_chunks: List[List[Item]],
    process_func: callable,
    max_workers: int = 4
) -> List[Any]:
    """
    Параллельная обработка данных

    Args:
        data_chunks: список чанков данных
        process_func: функция обработки
        max_workers: максимальное количество воркеров

    Returns:
        Результаты обработки
    """
    # Используем ProcessPoolExecutor для CPU-интенсивных задач
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()

        # Создаем задачи
        tasks = [
            loop.run_in_executor(executor, process_func, chunk)
            for chunk in data_chunks
        ]

        # Ждем завершения
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Фильтруем ошибки
    valid_results = [
        result for result in results
        if not isinstance(result, Exception)
    ]

    return valid_results


async def monitor_progress(
    task_name: str,
    total_items: int,
    progress_callback: Optional[callable] = None
) -> None:
    """
    Мониторинг прогресса выполнения задач

    Args:
        task_name: название задачи
        total_items: общее количество элементов
        progress_callback: функция обратного вызова для обновления прогресса
    """
    for i in range(total_items + 1):
        if progress_callback:
            progress_callback(task_name, i, total_items)

        if i < total_items:
            await asyncio.sleep(0.1)  # Имитация работы
        else:
            if progress_callback:
                progress_callback(task_name, total_items, total_items, completed=True)