"""
Генератор реалистичных тестовых данных для seed.json
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

# Константы для генерации
COURSES = [
    {
        "id": "python101",
        "title": "Python для начинающих",
        "description": "Основы программирования на Python",
        "topics": ["синтаксис", "типы данных", "функции", "ООП", "исключения"],
        "level": "beginner"
    },
    {
        "id": "ds_intro",
        "title": "Введение в Data Science",
        "description": "Основы анализа данных и машинного обучения",
        "topics": ["pandas", "numpy", "визуализация", "статистика", "ML basics"],
        "level": "intermediate"
    },
    {
        "id": "web_dev",
        "title": "Веб-разработка на Django",
        "description": "Создание веб-приложений с Django и React",
        "topics": ["HTML/CSS", "Django", "REST API", "React", "базы данных"],
        "level": "advanced"
    },
    {
        "id": "algorithms",
        "title": "Алгоритмы и структуры данных",
        "description": "Классические алгоритмы и структуры данных",
        "topics": ["сортировка", "поиск", "графы", "динамическое программирование", "деревья"],
        "level": "advanced"
    }
]

TOPICS = [
    "синтаксис", "типы данных", "функции", "ООП", "исключения",
    "pandas", "numpy", "визуализация", "статистика", "ML basics",
    "HTML/CSS", "Django", "REST API", "React", "базы данных",
    "сортировка", "поиск", "графы", "динамическое программирование", "деревья"
]

TAGS = [
    "легкий", "средний", "сложный", "теория", "практика",
    "код", "выбор", "сопоставление", "открытый", "алгоритм",
    "оптимизация", "база данных", "веб", "мобильный", "безопасность",
    "тестирование", "debug", "производительность", "память", "сеть"
]

ITEM_TYPES = [
    "multiple_choice", "single_choice", "open_answer",
    "code", "true_false", "matching"
]

DIFFICULTY_LEVELS = [1, 2, 3, 4, 5]

FIRST_NAMES = ["Алексей", "Мария", "Иван", "Екатерина", "Дмитрий", "Анна",
               "Сергей", "Ольга", "Андрей", "Наталья", "Михаил", "Елена",
               "Павел", "Юлия", "Александр", "Татьяна", "Владимир", "Светлана",
               "Николай", "Ирина", "Артем", "Виктория", "Роман", "Анастасия"]

LAST_NAMES = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов",
              "Попов", "Васильев", "Соколов", "Михайлов", "Новиков",
              "Федоров", "Морозов", "Волков", "Алексеев", "Лебедев"]

DOMAINS = ["gmail.com", "mail.ru", "yandex.ru", "outlook.com", "hotmail.com"]


def generate_user_id():
    """Генерация ID пользователя"""
    return f"user_{uuid.uuid4().hex[:8]}"


def generate_item_id():
    """Генерация ID вопроса"""
    return f"item_{uuid.uuid4().hex[:8]}"


def generate_course_id():
    """Генерация ID курса"""
    return f"course_{uuid.uuid4().hex[:6]}"


def generate_lesson_id(course_id):
    """Генерация ID урока"""
    return f"lesson_{course_id}_{uuid.uuid4().hex[:4]}"


def generate_timestamp(days_back=365):
    """Генерация случайной временной метки"""
    random_days = random.randint(0, days_back)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    random_seconds = random.randint(0, 59)

    dt = datetime.now() - timedelta(
        days=random_days,
        hours=random_hours,
        minutes=random_minutes,
        seconds=random_seconds
    )

    return dt.isoformat()


def generate_courses(num_courses=4):
    """Генерация курсов"""
    courses = []

    for i in range(min(num_courses, len(COURSES))):
        course = COURSES[i].copy()
        course["created_at"] = generate_timestamp(30)
        course["updated_at"] = generate_timestamp(7)
        course["is_active"] = random.choice([True, False])
        courses.append(course)

    return courses


def generate_lessons(courses, lessons_per_course=4):
    """Генерация уроков"""
    lessons = []

    for course in courses:
        course_topics = course["topics"]

        for i in range(lessons_per_course):
            lesson_id = generate_lesson_id(course["id"])

            lesson = {
                "id": lesson_id,
                "course_id": course["id"],
                "title": f"Урок {i + 1}: {random.choice(course_topics)}",
                "order": i + 1,
                "topic": random.choice(course_topics),
                "content": f"Содержание урока {i + 1} по курсу {course['title']}",
                "duration_minutes": random.choice([30, 45, 60, 90, 120]),
                "created_at": generate_timestamp(20)
            }
            lessons.append(lesson)

    return lessons


def generate_items(lessons, items_per_lesson=15):
    """Генерация вопросов"""
    items = []

    for lesson in lessons:
        for i in range(items_per_lesson):
            item_type = random.choice(ITEM_TYPES)
            difficulty = random.choice(DIFFICULTY_LEVELS)
            topic = lesson["topic"]

            # Генерация тегов в зависимости от сложности и типа
            num_tags = random.randint(1, 4)
            item_tags = random.sample(TAGS, num_tags)

            # Контент в зависимости от типа вопроса
            if item_type in ["multiple_choice", "single_choice"]:
                content = {
                    "question": f"Вопрос {i + 1} по теме '{topic}'",
                    "options": ["Вариант A", "Вариант B", "Вариант C", "Вариант D"],
                    "correct_answer": random.randint(0, 3),
                    "explanation": f"Объяснение к вопросу {i + 1}"
                }
            elif item_type == "open_answer":
                content = {
                    "question": f"Объясните понятие '{topic}'",
                    "max_length": random.choice([100, 200, 500]),
                    "sample_answer": f"Пример ответа на вопрос о {topic}"
                }
            elif item_type == "code":
                content = {
                    "question": f"Напишите код для решения задачи по {topic}",
                    "language": "python",
                    "test_cases": [
                        {"input": "test1", "output": "result1"},
                        {"input": "test2", "output": "result2"}
                    ]
                }
            elif item_type == "true_false":
                content = {
                    "question": f"Утверждение о {topic}",
                    "statement": f"Это утверждение о {topic}",
                    "is_true": random.choice([True, False])
                }
            elif item_type == "matching":
                content = {
                    "question": f"Сопоставьте элементы по теме '{topic}'",
                    "left_items": ["Элемент 1", "Элемент 2", "Элемент 3"],
                    "right_items": ["Соответствие 1", "Соответствие 2", "Соответствие 3"],
                    "correct_mapping": {"0": "0", "1": "1", "2": "2"}
                }

            item = {
                "id": generate_item_id(),
                "lesson_id": lesson["id"],
                "type": item_type,
                "difficulty": difficulty,
                "topic": topic,
                "tags": item_tags,
                "content": content,
                "metadata": {
                    "author": f"Преподаватель {random.choice(LAST_NAMES)}",
                    "generated": True
                },
                "created_at": generate_timestamp(10),
                "updated_at": generate_timestamp(3)
            }
            items.append(item)

    return items


def generate_users(num_users=45, teacher_ratio=0.1):
    """Генерация пользователей"""
    users = []
    num_teachers = int(num_users * teacher_ratio)

    for i in range(num_users):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        domain = random.choice(DOMAINS)

        if i < num_teachers:
            role = random.choice(["teacher", "admin"])
        else:
            role = "student"

        user = {
            "id": generate_user_id(),
            "email": f"{first_name.lower()}.{last_name.lower()}{i}@{domain}",
            "name": f"{first_name} {last_name}",
            "role": role,
            "group": f"Группа {random.randint(1, 5)}" if role == "student" else "",
            "created_at": generate_timestamp(100)
        }
        users.append(user)

    return users


def generate_blueprints(courses, num_blueprints=5):
    """Генерация черновиков квизов"""
    blueprints = []

    for i in range(num_blueprints):
        course = random.choice(courses)
        course_topics = course["topics"]

        # Выбираем случайные темы из курса (1-3 темы)
        num_topics = random.randint(1, 3)
        selected_topics = random.sample(course_topics, min(num_topics, len(course_topics)))

        # Правила для blueprint
        rules = {
            "topics": selected_topics,
            "difficulty": [random.randint(1, 3), random.randint(3, 5)],
            "types": random.sample(ITEM_TYPES, random.randint(2, 4)),
            "count": random.choice([10, 15, 20, 25]),
            "sort_by_difficulty": random.choice([True, False])
        }

        blueprint = {
            "id": f"bp_{uuid.uuid4().hex[:6]}",
            "name": f"Тест по курсу '{course['title']}'",
            "description": f"Итоговый тест по темам: {', '.join(selected_topics)}",
            "course_id": course["id"],
            "rules": rules,
            "tags": random.sample(TAGS, random.randint(2, 5)),
            "time_limit_minutes": random.choice([30, 45, 60, 90, 120]),
            "shuffle_questions": random.choice([True, False]),
            "shuffle_answers": random.choice([True, False]),
            "allow_back": random.choice([True, False]),
            "negative_marking": random.choice([True, False]),
            "created_at": generate_timestamp(30)
        }
        blueprints.append(blueprint)

    return blueprints


def generate_rules():
    """Генерация правил оценки"""
    rules = [
        {
            "id": "rule_multiple_choice",
            "name": "Оценка множественного выбора",
            "condition": {"type": "multiple_choice"},
            "action": {"correct": 1, "incorrect": 0, "penalty": 0.25}
        },
        {
            "id": "rule_single_choice",
            "name": "Оценка одиночного выбора",
            "condition": {"type": "single_choice"},
            "action": {"correct": 1, "incorrect": 0, "penalty": 0}
        },
        {
            "id": "rule_open_answer",
            "name": "Оценка открытого ответа",
            "condition": {"type": "open_answer"},
            "action": {"max": 5, "min": 0, "partial_credit": True}
        },
        {
            "id": "rule_code",
            "name": "Оценка кода",
            "condition": {"type": "code"},
            "action": {"per_test_case": 1, "max": 10, "compile_error": 0}
        },
        {
            "id": "rule_true_false",
            "name": "Оценка верно/неверно",
            "condition": {"type": "true_false"},
            "action": {"correct": 1, "incorrect": -0.5, "penalty": 0.5}
        },
        {
            "id": "rule_matching",
            "name": "Оценка сопоставления",
            "condition": {"type": "matching"},
            "action": {"per_match": 0.33, "max": 1, "min": 0}
        }
    ]
    return rules


def main():
    """Генерация всех данных и сохранение в seed.json"""
    print("Генерация тестовых данных...")

    # Генерация данных
    courses = generate_courses(4)
    print(f"Сгенерировано курсов: {len(courses)}")

    lessons = generate_lessons(courses, lessons_per_course=3)
    print(f"Сгенерировано уроков: {len(lessons)}")

    items = generate_items(lessons, items_per_lesson=17)
    print(f"Сгенерировано вопросов: {len(items)}")

    users = generate_users(45, teacher_ratio=0.1)
    print(
        f"Сгенерировано пользователей: {len(users)} (преподавателей: {len([u for u in users if u['role'] in ['teacher', 'admin']])})")

    blueprints = generate_blueprints(courses, num_blueprints=5)
    print(f"Сгенерировано черновиков: {len(blueprints)}")

    rules = generate_rules()
    print(f"Сгенерировано правил: {len(rules)}")

    # Сбор всех данных
    seed_data = {
        "courses": courses,
        "lessons": lessons,
        "items": items,
        "users": users,
        "blueprints": blueprints,
        "rules": rules,
        "generated_at": datetime.now().isoformat(),
        "metadata": {
            "total_items": len(items),
            "total_users": len(users),
            "total_courses": len(courses),
            "total_lessons": len(lessons),
            "total_blueprints": len(blueprints),
            "difficulty_distribution": {
                str(d): len([i for i in items if i["difficulty"] == d])
                for d in DIFFICULTY_LEVELS
            },
            "type_distribution": {
                t: len([i for i in items if i["type"] == t])
                for t in ITEM_TYPES
            }
        }
    }

    # Сохранение в файл
    output_file = "seed.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(seed_data, f, ensure_ascii=False, indent=2, default=str)

    print(f"\nДанные успешно сохранены в {output_file}")
    print("\nСтатистика:")
    print(f"  • Курсы: {len(courses)}")
    print(f"  • Уроки: {len(lessons)}")
    print(f"  • Вопросы: {len(items)}")
    print(f"  • Пользователи: {len(users)}")
    print(f"  • Черновики: {len(blueprints)}")
    print(f"  • Правила: {len(rules)}")

    # Вывод распределения по сложности
    print("\nРаспределение вопросов по сложности:")
    for d in DIFFICULTY_LEVELS:
        count = len([i for i in items if i["difficulty"] == d])
        print(f"  • Сложность {d}: {count} вопросов")

    # Вывод распределения по типам
    print("\nРаспределение по типам вопросов:")
    for t in ITEM_TYPES:
        count = len([i for i in items if i["type"] == t])
        print(f"  • {t}: {count} вопросов")

    return seed_data


if __name__ == "__main__":
    main()