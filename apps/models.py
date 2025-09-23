from django.db import models

class Course(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=200)
    topics = models.JSONField(default=list)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class User(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
    ]
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.role})"

class Item(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    TYPE_CHOICES = [
        ("mcq/single", "MCQ Single"),
        ("mcq/multi", "MCQ Multi"),
        ("short", "Short"),
        ("numeric", "Numeric"),
        ("ordering", "Ordering"),
        ("matching", "Matching"),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name="items")
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    stem = models.TextField()
    options = models.JSONField(default=list)
    answer = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    difficulty = models.IntegerField()

    def __str__(self):
        return f"{self.type} - {self.stem[:30]}"

class QuizBlueprint(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name="blueprints")
    rules = models.JSONField(default=dict)

    def __str__(self):
        return f"Blueprint {self.id}"

class Quiz(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("started", "Started"),
        ("finished", "Finished"),
        ("graded", "Graded"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quizzes")
    blueprint = models.ForeignKey(QuizBlueprint, on_delete=models.CASCADE, related_name="quizzes")
    items = models.ManyToManyField(Item)
    ts = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="started")

    def __str__(self):
        return f"Quiz {self.id} - {self.status}"

class Answer(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="answers")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="answers")
    payload = models.JSONField(default=list)

    def __str__(self):
        return f"Answer {self.id} for Quiz {self.quiz.id}"

class Grade(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="grades")
    score = models.FloatField()
    breakdown = models.JSONField(default=list)

    def __str__(self):
        return f"Grade {self.score} for Quiz {self.quiz.id}"

class Event(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=20)
    ts = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(default=dict)

    def __str__(self):
        return f"Event {self.name} at {self.ts}"

class Rule(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    kind = models.CharField(max_length=20)
    payload = models.JSONField(default=dict)

    def __str__(self):
        return f"Rule {self.kind}"