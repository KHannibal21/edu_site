import json
import random
from django.core.management.base import BaseCommand
from apps.models import *


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными для образовательной платформы'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')

        # Очищаем существующие данные
        self.clear_data()

        # Создаем курсы
        courses = self.create_courses()

        # Создаем уроки
        lessons = self.create_lessons(courses)

        # Создаем задания (≥200)
        items = self.create_items(lessons)

        # Создаем пользователей (≥40)
        users = self.create_users()

        # Создаем blueprints (≥3)
        blueprints = self.create_blueprints(lessons)

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно создано: {len(courses)} курсов, {len(lessons)} уроков, '
                f'{len(items)} заданий, {len(users)} пользователей, {len(blueprints)} шаблонов'
            )
        )

    def clear_data(self):
        """Очистка существующих данных"""
        models = [Course, Lesson, Item, User, QuizBlueprint, Quiz, Answer, Grade, Event, Rule]
        for model in models:
            model.objects.all().delete()

    def create_courses(self):
        """Создание курсов (≥3)"""
        courses_data = [
            {"id": "course1", "title": "Python Basics", "topics": ["programming", "python", "basics"]},
            {"id": "course2", "title": "Web Development", "topics": ["web", "django", "flask", "html", "css"]},
            {"id": "course3", "title": "Data Science",
             "topics": ["data", "analysis", "pandas", "numpy", "visualization"]},
            {"id": "course4", "title": "Algorithms", "topics": ["algorithms", "data structures", "complexity"]},
        ]

        courses = []
        for data in courses_data:
            course = Course.objects.create(
                id=data["id"],
                title=data["title"],
                topics=data["topics"]
            )
            courses.append(course)

        return courses

    def create_lessons(self, courses):
        """Создание уроков (≥12)"""
        lessons_data = []
        lesson_counter = 1

        for course in courses:
            for i in range(3):  # по 3 урока на курс
                lessons_data.append({
                    "id": f"lesson{lesson_counter}",
                    "course": course,
                    "title": f"{course.title} - Урок {i + 1}",
                    "topic": random.choice(course.topics)
                })
                lesson_counter += 1

        lessons = []
        for data in lessons_data:
            lesson = Lesson.objects.create(
                id=data["id"],
                course=data["course"],
                title=data["title"],
                topic=data["topic"]
            )
            lessons.append(lesson)

        return lessons

    def create_items(self, lessons):
        """Создание заданий (≥200)"""
        items = []
        item_types = ['mcq/single', 'mcq/multi', 'short', 'numeric', 'ordering', 'matching']

        for i in range(1, 201):  # 200 заданий
            item_id = f"item{i:03d}"
            lesson = random.choice(lessons) if random.random() > 0.1 else None  # 10% без урока
            item_type = random.choice(item_types)

            # Генерация вариантов ответов в зависимости от типа
            if item_type in ['mcq/single', 'mcq/multi']:
                options = [f"Вариант {chr(65 + j)}" for j in range(4)]
                if item_type == 'mcq/single':
                    answer = [random.randint(0, 3)]
                else:  # mcq/multi
                    answer = sorted(random.sample(range(4), random.randint(1, 3)))
            elif item_type == 'short':
                options = []
                answer = "Пример правильного ответа"
            elif item_type == 'numeric':
                options = []
                answer = random.randint(1, 100)
            elif item_type == 'ordering':
                options = [f"Элемент {j + 1}" for j in range(4)]
                answer = list(range(4))
                random.shuffle(answer)  # правильный порядок
            else:  # matching
                options = [f"Левый {j + 1}" for j in range(3)] + [f"Правый {j + 1}" for j in range(3)]
                answer = list(range(3))  # соответствия

            # Теги на основе темы урока
            tags = [lesson.topic] if lesson else ["general"]
            if random.random() > 0.7:  # 30% chance добавить дополнительный тег
                tags.append("advanced" if random.random() > 0.5 else "basic")

            item = Item.objects.create(
                id=item_id,
                lesson=lesson,
                type=item_type,
                stem=f"Вопрос {i}: Что из перечисленного верно?",
                options=options,
                answer=answer,
                tags=tags,
                difficulty=random.randint(1, 5)
            )
            items.append(item)

        # Добавляем еще несколько заданий чтобы было >200
        for i in range(201, 211):
            item = Item.objects.create(
                id=f"item{i:03d}",
                lesson=None,
                type=random.choice(item_types),
                stem=f"Дополнительный вопрос {i}",
                options=[],
                answer=[],
                tags=["additional"],
                difficulty=random.randint(1, 5)
            )
            items.append(item)

        return items

    def create_users(self):
        """Создание пользователей (≥40)"""
        users = []

        # Создаем преподавателей (5)
        teachers = [
            {"id": "teacher1", "name": "Профессор Иванов", "role": "teacher"},
            {"id": "teacher2", "name": "Доцент Петрова", "role": "teacher"},
            {"id": "teacher3", "name": "Преподаватель Сидоров", "role": "teacher"},
            {"id": "teacher4", "name": "Доктор наук Кузнецов", "role": "teacher"},
            {"id": "teacher5", "name": "Кандидат наук Смирнова", "role": "teacher"},
        ]

        for data in teachers:
            user = User.objects.create(
                id=data["id"],
                name=data["name"],
                role=data["role"]
            )
            users.append(user)

        # Создаем студентов (35+)
        for i in range(1, 36):
            user = User.objects.create(
                id=f"student{i:03d}",
                name=f"Студент {i}",
                role="student"
            )
            users.append(user)

        return users

    def create_blueprints(self, lessons):
        """Создание шаблонов тестов (≥3)"""
        blueprints_data = [
            {
                "id": "bp_basic",
                "lesson": None,
                "rules": {
                    "count": 10,
                    "difficulty": [1, 2],
                    "topics": ["python", "basics"],
                    "mix": True
                }
            },
            {
                "id": "bp_advanced",
                "lesson": None,
                "rules": {
                    "count": 15,
                    "difficulty": [3, 5],
                    "topics": ["django", "algorithms", "data"],
                    "types": ["mcq/single", "mcq/multi"],
                    "mix": False
                }
            },
            {
                "id": "bp_mixed",
                "lesson": random.choice(lessons),
                "rules": {
                    "count": 20,
                    "difficulty": [1, 5],
                    "mix": True
                }
            },
            {
                "id": "bp_quick",
                "lesson": None,
                "rules": {
                    "count": 5,
                    "mix": True
                }
            }
        ]

        blueprints = []
        for data in blueprints_data:
            blueprint = QuizBlueprint.objects.create(
                id=data["id"],
                lesson=data["lesson"],
                rules=data["rules"]
            )
            blueprints.append(blueprint)

        return blueprints