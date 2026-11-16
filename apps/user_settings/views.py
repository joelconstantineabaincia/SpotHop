import json
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from apps.home.models import User
from apps.login.auth_helper import login_required, get_logged_in_user


@login_required
def settings_view(request):
    user = get_logged_in_user(request)

    if request.method == "POST":
        preferred_noise = request.POST.get("preferred_noise_level", "QUIET").strip()
        preferred_outlets = request.POST.get("preferred_outlet_density", "PLENTIFUL").strip()
        min_wifi = request.POST.get("min_wifi_speed_mbps", "20.0").strip()
        dark_mode = "dark_mode" in request.POST
        email_notifications = "email_notifications" in request.POST

        user.preferred_noise_level = preferred_noise
        user.preferred_outlet_density = preferred_outlets
        try:
            user.min_wifi_speed_mbps = Decimal(min_wifi) if min_wifi else Decimal("20.00")
        except Exception:
            user.min_wifi_speed_mbps = Decimal("20.00")
        user.dark_mode = dark_mode
        user.email_notifications = email_notifications
        user.save()

        # Update session dark_mode
        request.session['dark_mode'] = dark_mode

        messages.success(request, "Your study preferences and application settings have been updated.")
        return redirect("user_settings:user_settings")

    return render(request, "user_settings/user_settings.html", {"settings_user": user})


@login_required
def toggle_dark_mode_view(request):
    """
    Quick asynchronous toggle endpoint for instant navbar theme toggle.
    """
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            dark_mode = bool(data.get('dark_mode', not user.dark_mode))
        except Exception:
            dark_mode = not user.dark_mode

        user.dark_mode = dark_mode
        user.save()
        request.session['dark_mode'] = dark_mode
        return JsonResponse({'success': True, 'dark_mode': dark_mode})

    return JsonResponse({'dark_mode': user.dark_mode})
