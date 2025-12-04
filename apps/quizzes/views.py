from django.shortcuts import render

def quizzes(request):
    return render(request, 'apps/quizzes/quizzes.html')