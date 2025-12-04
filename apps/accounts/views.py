from django.shortcuts import render

def login_page(request):
    return render(request, 'apps/accounts/login.html')

def register_page(request):
    return render(request, 'apps/accounts/register.html')

def logout_page(request):
    # Пока просто заглушка
    from django.shortcuts import redirect
    from django.urls import reverse
    return redirect(reverse('home:home'))