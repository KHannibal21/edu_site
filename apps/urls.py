from django.urls import path
from . import views

app_name = 'apps'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('data/', views.data_explorer, name='data'),
    path('functional/', views.functional_core, name='functional'),
    path('quiz/<str:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('api/generate-quiz/', views.generate_quiz_ajax, name='generate_quiz'),
]