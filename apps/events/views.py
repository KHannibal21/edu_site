from django.shortcuts import render

def events(request):
    return render(request, 'apps/events/events.html')