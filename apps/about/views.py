from django.shortcuts import render

def about(request):
    return render(request, 'apps/about/about.html')