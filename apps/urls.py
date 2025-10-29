from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView, LoginView

app_name = 'apps'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('data/', views.data_explorer, name='data'),
    path('functional/', views.functional_core, name='functional'),
    path('pipelines/', views.pipelines_demo, name='pipelines'),
    path('reports/', views.reports_view, name='reports'),
    path('quiz/<str:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('api/generate-quiz/', views.generate_quiz_ajax, name='generate_quiz'),
    # Вход через стандартный LoginView
    path('login/', LoginView.as_view(template_name='apps/login.html'), name='login'),

    # Регистрация через кастомный view
    path('register/', views.register_view, name='register'),

    path('logout/', LogoutView.as_view(next_page='apps:functional'), name='logout'),


]