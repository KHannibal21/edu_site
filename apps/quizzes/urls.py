from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.quizzes, name='quizzes'),
]