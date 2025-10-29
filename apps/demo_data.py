from django.utils import timezone
from .models import Course, Lesson, User, Item, QuizBlueprint, Quiz, Answer, GradingRule
import random


def create_demo_grading_rules():
    """Создание демо-правил оценивания если их нет"""
    if not GradingRule.objects.exists():
        rules_data = [
            ('mcq/single', 'Точное совпадение', 'exact_match', 1.0, {}),
            ('mcq/multi', 'Частичное оценивание', 'partial', 1.5, {'penalty_per_wrong': 0.25}),
            ('short', 'Нечеткое совпадение', 'fuzzy_match', 1.0, {}),
            ('numeric', 'Точное число', 'exact_match', 1.0, {}),
        ]

        for i, (item_type, name, func, weight, params) in enumerate(rules_data):
            GradingRule.objects.create(
                id=f"rule_{i + 1}",
                item_type=item_type,
                name=name,
                scoring_function=func,
                weight=weight,
                parameters=params
            )
        print("✅ Демо-правила оценивания созданы")


def create_demo_course_structure():
    """Создание демо-курса и уроков если их нет"""
    if not Course.objects.exists():
        course = Course.objects.create(
            id="demo_course",
            title="Python Programming",
            topics=["python", "programming", "algorithms"]
        )

        Lesson.objects.create(
            id="demo_lesson1",
            course=course,
            title="Введение в Python",
            topic="python"
        )

        Lesson.objects.create(
            id="demo_lesson2",
            course=course,
            title="Функции в Python",
            topic="python"
        )
        print("✅ Демо-курс и уроки созданы")


def create_demo_items():
    """Создание демо-заданий если их нет"""
    if not Item.objects.exists():
        lesson = Lesson.objects.first()

        demo_items = [
            {
                'id': 'item_1',
                'type': 'mcq/single',
                'stem': 'Какой тип данных в Python является изменяемым?',
                'options': ['Список', 'Кортеж', 'Строка', 'Число'],
                'answer': [0],  # Список
                'tags': ['python', 'basic'],
                'difficulty': 2
            },
            {
                'id': 'item_2',
                'type': 'mcq/multi',
                'stem': 'Какие из перечисленных являются структурами данных в Python?',
                'options': ['Список', 'Словарь', 'Массив', 'Множество'],
                'answer': [0, 1, 3],  # Список, Словарь, Множество
                'tags': ['python', 'data_structures'],
                'difficulty': 3
            },
            {
                'id': 'item_3',
                'type': 'short',
                'stem': 'Как называется функция для получения длины последовательности в Python?',
                'options': [],
                'answer': ['len'],
                'tags': ['python', 'functions'],
                'difficulty': 1
            },
            {
                'id': 'item_4',
                'type': 'numeric',
                'stem': 'Чему равно 2 в степени 10?',
                'options': [],
                'answer': [1024],
                'tags': ['math', 'python'],
                'difficulty': 2
            }
        ]

        for item_data in demo_items:
            Item.objects.create(
                id=item_data['id'],
                lesson=lesson,
                type=item_data['type'],
                stem=item_data['stem'],
                options=item_data['options'],
                answer=item_data['answer'],
                tags=item_data['tags'],
                difficulty=item_data['difficulty']
            )
        print("✅ Демо-задания созданы")


def create_demo_user():
    """Создание демо-пользователя если нет"""
    if not User.objects.exists():
        user = User.objects.create(
            id="demo_user",
            name="Демо Студент",
            role="student"
        )
        print("✅ Демо-пользователь создан")
        return user
    return User.objects.first()


def create_demo_blueprint():
    """Создание демо-шаблона теста если нет"""
    if not QuizBlueprint.objects.exists():
        lesson = Lesson.objects.first()
        blueprint = QuizBlueprint.objects.create(
            id="demo_bp",
            lesson=lesson,
            rules={
                "difficulty": [1, 5],
                "count": 4,
                "topics": ["python"],
                "types": ["mcq/single", "mcq/multi", "short", "numeric"],
                "mix": True
            }
        )
        print("✅ Демо-шаблон теста создан")
        return blueprint
    return QuizBlueprint.objects.first()


def create_simple_demo_quiz():
    """Простое создание демо-теста без циклических импортов"""

    # Создаем все необходимые демо-данные
    create_demo_grading_rules()
    create_demo_course_structure()
    create_demo_items()
    user = create_demo_user()
    blueprint = create_demo_blueprint()

    # Создаем квиз вручную
    quiz_id = f"demo_quiz_{random.randint(1000, 9999)}"
    quiz = Quiz.objects.create(
        id=quiz_id,
        user=user,
        blueprint=blueprint,
        status="finished"
    )

    # Добавляем случайные задания
    demo_items = Item.objects.all()[:4]
    quiz.items.set(demo_items)
    print(f"✅ Демо-тест создан: {quiz.id}")

    # Добавляем демо-ответы
    for i, item in enumerate(quiz.items.all()):
        # Чередуем правильные и неправильные ответы для демонстрации
        if i % 2 == 0:
            # Правильный ответ
            payload = item.answer
        else:
            # Неправильный ответ для демонстрации оценки
            if item.type == 'mcq/single':
                payload = [1] if len(item.options) > 1 else [0]  # Выбираем второй вариант
            elif item.type == 'mcq/multi':
                payload = [0] if item.options else []  # Только первый вариант
            else:
                payload = "неправильный ответ"

        Answer.objects.create(
            id=f"demo_answer_{quiz.id}_{i + 1}",
            quiz=quiz,
            item=item,
            payload=payload,
            is_graded=False
        )
    print("✅ Демо-ответы созданы")

    return quiz