import pytest
from apps.models import Item, Quiz, User, QuizBlueprint, Grade
from apps.services import safe_item, validate_answer, grade_item, grade_quiz_pipeline
from apps.ftypes import Maybe, Either


@pytest.fixture
def setup_data(db):
    """Создаем минимальные данные для тестов"""
    user = User.objects.create(id="u1", name="Test User", role="student")

    blueprint = QuizBlueprint.objects.create(
        id="bp1",
        rules={"count": 3, "difficulty": [1, 2], "mix": True}
    )

    # Создаем тестовые вопросы
    for i in range(1, 6):
        Item.objects.create(
            id=f"item{i}",
            type="mcq/single",
            stem=f"Question {i}",
            options=["Option A", "Option B", "Option C"],
            answer=[0],  # Правильный ответ - первый вариант
            tags=["python", "test"],
            difficulty=i % 3 + 1  # Сложность от 1 до 3
        )
    return user, blueprint, Item.objects.all()


def test_safe_item_returns_maybe_for_existing_item(setup_data):
    """Тест 1: safe_item возвращает Just для существующего задания"""
    user, blueprint, items = setup_data
    items_tuple = tuple(items)

    result = safe_item(items_tuple, "item1")

    assert isinstance(result, Maybe)
    assert result.is_just()
    assert result.get_or_else(None).id == "item1"


def test_safe_item_returns_nothing_for_non_existent(setup_data):
    """Тест 2: safe_item возвращает Nothing для несуществующего задания"""
    user, blueprint, items = setup_data
    items_tuple = tuple(items)

    result = safe_item(items_tuple, "non_existent")

    assert isinstance(result, Maybe)
    assert result.is_nothing()


def test_validate_answer_returns_right_for_valid_mcq_answer(setup_data):
    """Тест 3: validate_answer возвращает Right для валидного MCQ ответа"""
    user, blueprint, items = setup_data
    item = items[0]  # mcq/single

    result = validate_answer(item, [0], ())

    assert isinstance(result, Either)
    assert result.is_right()
    assert result.get_or_else(None) == [0]


def test_validate_answer_returns_left_for_invalid_mcq_answer(setup_data):
    """Тест 4: validate_answer возвращает Left для невалидного MCQ ответа"""
    user, blueprint, items = setup_data
    item = items[0]  # mcq/single

    result = validate_answer(item, "invalid_string", ())

    assert isinstance(result, Either)
    assert result.is_left()
    # Исправленная проверка - получаем значение из Left
    error_data = result.get_or_else("no_error")
    assert "error" in error_data  # Теперь error_data будет словарем с ошибкой


def test_grade_item_returns_right_with_score_for_correct_answer(setup_data):
    """Тест 5: grade_item возвращает Right с баллами за правильный ответ"""
    user, blueprint, items = setup_data
    item = items[0]  # mcq/single с answer=[0]

    result = grade_item(item, [0], ())

    assert isinstance(result, Either)
    assert result.is_right()
    assert result.get_or_else(0) == 1.0  # Полный балл за правильный ответ


def test_grade_quiz_pipeline_creates_grade_for_valid_answers(setup_data):
    """Тест 6: grade_quiz_pipeline создает Grade для валидных ответов"""
    user, blueprint, items = setup_data
    quiz = Quiz.objects.create(id="q1", user=user, blueprint=blueprint, status="completed")
    items_tuple = tuple(items)

    # Создаем ответы (правильные)
    answers = {
        "item1": [0],  # Правильный ответ
        "item2": [0],  # Правильный ответ
    }

    result = grade_quiz_pipeline(quiz, answers, items_tuple, ())

    assert isinstance(result, Either)
    assert result.is_right()

    grade = result.get_or_else(None)
    assert isinstance(grade, Grade)
    assert grade.score == 1.0  # Оба ответа правильные