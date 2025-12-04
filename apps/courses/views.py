from django.shortcuts import render

def courses(request):
    return render(request, 'apps/courses/courses.html')