from django.shortcuts import render, redirect
from django.contrib import messages
from apps.home.models import User, CheckIn, Review, SavedSpot
from apps.login.auth_helper import login_required, get_logged_in_user


@login_required
def profile_view(request):
    user = get_logged_in_user(request)

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        bio = request.POST.get("bio", "").strip()

        user.full_name = full_name
        user.bio = bio
        user.save()
        messages.success(request, "Your profile details have been updated successfully.")
        return redirect("profile:profile")

    check_ins = CheckIn.objects.filter(user=user).select_related('spot').order_by('-checked_in_at')
    reviews = Review.objects.filter(user=user).select_related('spot').order_by('-id')
    saved_spots_count = SavedSpot.objects.filter(user=user).count()

    context = {
        'profile_user': user,
        'check_ins': check_ins,
        'reviews': reviews,
        'saved_spots_count': saved_spots_count,
        'active_checkin': check_ins.filter(is_active=True).first(),
    }
    return render(request, "user_profile/user_profile.html", context)
