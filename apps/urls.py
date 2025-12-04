from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.home.urls')),
    path('about/', include('apps.about.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('courses/', include('apps.courses.urls')),
    path('events/', include('apps.events.urls')),
    path('quizzes/', include('apps.quizzes.urls')),
    path('users/', include('apps.users.urls')),
    path('analytics/', include('apps.analytics.urls')),
]