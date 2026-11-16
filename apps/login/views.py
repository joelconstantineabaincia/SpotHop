from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from apps.home.models import User
from .auth_helper import login_user, logout_user

def login_view(request):
    if request.session.get('user_id'):
        return redirect('home:home')

    next_url = request.GET.get('next', '')
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        next_url = request.POST.get("next", "") or next_url

        if not username or not password:
            return render(request, "login/login.html", {
                "error": "Please enter both username and password.",
                "username": username,
                "next": next_url,
            })

        user = User.objects.filter(username=username).first()
        if user and check_password(password, user.password_hash):
            login_user(request, user)
            messages.success(request, f"Welcome back, {user.full_name or user.username}!")
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect("home:home")
        else:
            return render(request, "login/login.html", {
                "error": "Invalid username or password.",
                "username": username,
                "next": next_url,
            })

    return render(request, "login/login.html", {"next": next_url})

def logout_view(request):
    logout_user(request)
    messages.info(request, "You have been logged out.")
    return redirect("login:login")
