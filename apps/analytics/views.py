from django.shortcuts import render

def analytics(request):
    return render(request, 'apps/analytics/analytics.html')