from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from apps.home.models import User
from apps.login.auth_helper import login_user

def register_view(request):
    if request.session.get('user_id'):
        return redirect('home:home')

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        full_name = request.POST.get("full_name", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        context = {
            "username": username,
            "email": email,
            "full_name": full_name,
        }

        if not username or not email or not password:
            context["error"] = "Please fill in all required fields."
            return render(request, "register/register.html", context)

        if len(password) < 6:
            context["error"] = "Password must be at least 6 characters long."
            return render(request, "register/register.html", context)

        if confirm_password and password != confirm_password:
            context["error"] = "Passwords do not match."
            return render(request, "register/register.html", context)

        if User.objects.filter(username__iexact=username).exists():
            context["error"] = "Username is already taken. Please choose another."
            return render(request, "register/register.html", context)

        if User.objects.filter(email__iexact=email).exists():
            context["error"] = "An account with this email already exists."
            return render(request, "register/register.html", context)

        # Create user record
        user = User.objects.create(
            username=username,
            email=email,
            password_hash=make_password(password),
            full_name=full_name or username,
            dark_mode=False,
            email_notifications=True,
            preferred_noise_level='QUIET',
            preferred_outlet_density='PLENTIFUL',
            min_wifi_speed_mbps=20.0
        )

        login_user(request, user)
        messages.success(request, f"Welcome to SpotHop, {user.full_name or user.username}! Your account has been created.")
        return redirect("home:home")

    return render(request, "register/register.html")
