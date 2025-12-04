"""
Иммутабельные модели данных (dataclasses с frozen=True)
Все поля доступны только для чтения
"""
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional, Any, Union
from datetime import datetime
import json
from enum import Enum


class ItemType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    OPEN_ANSWER = "open_answer"
    CODE = "code"
    TRUE_FALSE = "true_false"
    MATCHING = "matching"


class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class Difficulty(int, Enum):
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5


@dataclass(frozen=True)
class Course:
    id: str
    title: str
    description: str
    topics: Tuple[str, ...]
    created_at: str
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


@dataclass(frozen=True)
class Lesson:
    id: str
    course_id: str
    title: str
    order: int
    topic: str
    content: str
    duration_minutes: int
    created_at: str


@dataclass(frozen=True)
class Item:
    id: str
    lesson_id: str
    type: ItemType
    difficulty: Difficulty
    topic: str
    tags: Tuple[str, ...]
    content: Dict[str, Any]  # вопрос, варианты, правильный ответ и т.д.
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __hash__(self):
        return hash(self.id)

    def to_index(self) -> int:
        """Преобразование в индекс для кэширования"""
        return hash(self.id) % 1000000

    @classmethod
    def from_index(cls, idx: int, items_map: Dict[int, 'Item']) -> Optional['Item']:
        """Восстановление по индексу (для примера)"""
        return items_map.get(idx)


@dataclass(frozen=True)
class User:
    id: str
    email: str
    name: str
    role: UserRole
    group: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def is_teacher(self) -> bool:
        return self.role in [UserRole.TEACHER, UserRole.ADMIN]


@dataclass(frozen=True)
class QuizBlueprint:
    id: str
    name: str
    description: str
    course_id: str
    rules: Dict[str, Any]  # {topic: weight, difficulty: [min, max], count: N, ...}
    tags: Tuple[str, ...] = field(default_factory=tuple)
    time_limit_minutes: int = 60
    shuffle_questions: bool = True
    shuffle_answers: bool = True
    allow_back: bool = True
    negative_marking: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_key(self) -> str:
        """Иммутабельный ключ для кэширования"""
        rules_str = json.dumps(self.rules, sort_keys=True)
        return f"{self.id}_{rules_str}"


@dataclass(frozen=True)
class Quiz:
    id: str
    user_id: str
    blueprint_id: str
    items: Tuple[Item, ...]
    created_at: str
    started_at: Optional[str] = None
    submitted_at: Optional[str] = None
    status: str = "created"  # created, started, submitted, graded

    def start(self, start_time: str) -> 'Quiz':
        """Иммутабельное обновление - возвращаем новый объект"""
        return Quiz(
            id=self.id,
            user_id=self.user_id,
            blueprint_id=self.blueprint_id,
            items=self.items,
            created_at=self.created_at,
            started_at=start_time,
            submitted_at=self.submitted_at,
            status="started"
        )

    def submit(self, submit_time: str) -> 'Quiz':
        return Quiz(
            id=self.id,
            user_id=self.user_id,
            blueprint_id=self.blueprint_id,
            items=self.items,
            created_at=self.created_at,
            started_at=self.started_at,
            submitted_at=submit_time,
            status="submitted"
        )


@dataclass(frozen=True)
class Answer:
    id: str
    quiz_id: str
    item_id: str
    user_id: str
    content: Dict[str, Any]  # ответ пользователя
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Grade:
    id: str
    quiz_id: str
    user_id: str
    score: float
    max_score: float
    details: Dict[str, float] = field(default_factory=dict)  # item_id: score
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def percentage(self) -> float:
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0


@dataclass(frozen=True)
class Rule:
    id: str
    name: str
    condition: Dict[str, Any]  # например: {"type": "multiple_choice", "points": 1}
    action: Dict[str, Any]  # например: {"correct": 1, "incorrect": -0.25}

    def apply(self, item: Item, answer: Answer) -> float:
        """Применить правило к ответу"""
        # Базовая реализация
        if self.condition.get("type") == item.type.value:
            if answer.content.get("is_correct", False):
                return self.action.get("correct", 1)
            else:
                return self.action.get("incorrect", 0)
        return 0.0


@dataclass(frozen=True)
class SeedData:
    """Контейнер для всех данных из seed.json"""
    courses: Tuple[Course, ...]
    lessons: Tuple[Lesson, ...]
    items: Tuple[Item, ...]
    users: Tuple[User, ...]
    blueprints: Tuple[QuizBlueprint, ...]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SeedData':
        """Создание из словаря (например, из JSON)"""
        return cls(
            courses=tuple(Course(**c) for c in data.get("courses", [])),
            lessons=tuple(Lesson(**l) for l in data.get("lessons", [])),
            items=tuple(Item(**i) for i in data.get("items", [])),
            users=tuple(User(**u) for u in data.get("users", [])),
            blueprints=tuple(QuizBlueprint(**b) for b in data.get("blueprints", []))
        )