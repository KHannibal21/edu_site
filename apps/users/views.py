from django.shortcuts import render

def users(request):
    return render(request, 'apps/users/users.html')