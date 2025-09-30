import pytest
from apps.models import *
from apps.services import *
from apps.views import create_filter_factory, apply_filters

@pytest.fixture
def setup_data(db):
    """Создаем минимальные данные для тестов"""
    course = Course.objects.create(id="c1", title="Course", topics=["python"])
    lesson = Lesson.objects.create(id="l1", course=course, title="Lesson", topic="python")
    user = User.objects.create(id="u1", name="User", role="student")
    blueprint = QuizBlueprint.objects.create(
        id="bp1",
        lesson=lesson,
        rules={"count": 2, "difficulty": [1, 3], "mix": True}
    )

    for i in range(1, 6):
        Item.objects.create(
            id=f"item{i}",
            lesson=lesson,
            type="mcq/single",
            stem=f"Question {i}",
            options=["A", "B", "C"],
            answer=[0],
            tags=["python"],
            difficulty=i
        )
    return course, lesson, user, blueprint


def test_immutable_data_loading(setup_data):
    """Тест 1: Загрузка в иммутабельные структуры"""
    courses, items, blueprints, users = load_immutable_data()

    assert isinstance(items, tuple)
    assert all(isinstance(item, ImmutableItem) for item in items)
    assert isinstance(items[0].options, tuple)


def test_pick_items_uses_filter(setup_data):
    """Тест 2: pick_items использует filter"""
    _, items, blueprints, _ = load_immutable_data()
    bp = blueprints[0]  # difficulty [1,3]

    selected = pick_items_functional(items, bp)

    assert all(1 <= item.difficulty <= 3 for item in selected)


def test_calculate_statistics_uses_reduce(setup_data):
    """Тест 3: calculate_statistics использует reduce"""
    stats = calculate_statistics()

    assert stats['total_items'] == 5
    assert 'mcq/single' in stats['type_distribution']


def test_sum_score_uses_reduce(setup_data):
    """Тест 4: sum_score использует reduce"""
    _, _, user, blueprint = setup_data
    quiz = Quiz.objects.create(id="q1", user=user, blueprint=blueprint, status="started")
    Grade.objects.create(id="g1", quiz=quiz, score=5.0, breakdown=[])
    Grade.objects.create(id="g2", quiz=quiz, score=3.0, breakdown=[])

    grades = tuple(Grade.objects.all())
    total = sum_score(grades)

    assert total == 8.0


def test_hof_filter_factory(setup_data):
    """Тест 5: Функции высшего порядка"""
    _, items, _, _ = load_immutable_data()
    filter_func = create_filter_factory(difficulty_range=(2, 4))
    filtered = apply_filters(items, filter_func)

    assert all(2 <= item.difficulty <= 4 for item in filtered)


def test_ui_overview_works(setup_data):
    """Тест 6: UI Overview агрегаты работают"""
    stats = calculate_statistics()

    assert 'total_courses' in stats
    assert 'total_items' in stats
    assert 'type_distribution' in stats
    assert 'difficulty_distribution' in stats
    assert isinstance(stats['type_distribution'], dict)
    assert isinstance(stats['difficulty_distribution'], dict)
