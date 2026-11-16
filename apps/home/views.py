from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from django.utils import timezone
from apps.home.models import User, StudySpot, SpotAmenity, Review, CheckIn, SavedSpot
from apps.login.auth_helper import login_required, get_logged_in_user


def home_view(request):
    current_user = get_logged_in_user(request)

    # Base query with related amenities and precomputed counts
    spots_qs = StudySpot.objects.select_related('amenities').prefetch_related('reviews', 'check_ins').all()

    # Query params
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    price_tier = request.GET.get('price_tier', '').strip()
    outlet_density = request.GET.get('outlet_density', '').strip()
    predominant_noise = request.GET.get('predominant_noise', '').strip()
    min_wifi = request.GET.get('min_wifi', '').strip()
    open_now = request.GET.get('open_now', '').strip()
    match_prefs = request.GET.get('match_prefs', '').strip()
    sort_by = request.GET.get('sort_by', 'default').strip()

    # Match My Preferences logic
    if match_prefs == '1' and current_user:
        if current_user.preferred_noise_level:
            predominant_noise = current_user.preferred_noise_level
        if current_user.preferred_outlet_density:
            outlet_density = current_user.preferred_outlet_density
        if current_user.min_wifi_speed_mbps:
            min_wifi = str(current_user.min_wifi_speed_mbps)

    # Search filter
    if q:
        spots_qs = spots_qs.filter(
            Q(name__icontains=q) |
            Q(address__icontains=q) |
            Q(category__icontains=q)
        )

    # Category filter
    if category:
        spots_qs = spots_qs.filter(category=category)

    # Price tier filter
    if price_tier:
        spots_qs = spots_qs.filter(price_tier=price_tier)

    # Outlet density filter
    if outlet_density:
        spots_qs = spots_qs.filter(amenities__outlet_density=outlet_density)

    # Noise level filter
    if predominant_noise:
        spots_qs = spots_qs.filter(amenities__predominant_noise=predominant_noise)

    # Min Wi-Fi speed filter
    if min_wifi:
        try:
            min_wifi_val = Decimal(min_wifi)
            spots_qs = spots_qs.filter(amenities__avg_wifi_speed_mbps__gte=min_wifi_val)
        except Exception:
            pass

    # Annotate with rating and active check-ins count for sorting
    spots_qs = spots_qs.annotate(
        annotated_avg_rating=Avg('reviews__overall_rating'),
        annotated_review_count=Count('reviews', distinct=True),
        annotated_active_checkins=Count('check_ins', filter=Q(check_ins__is_active=True), distinct=True)
    )

    # Sorting
    if sort_by == 'rating':
        spots_qs = spots_qs.order_by('-annotated_avg_rating', '-annotated_review_count', 'name')
    elif sort_by == 'wifi':
        spots_qs = spots_qs.order_by('-amenities__avg_wifi_speed_mbps', 'name')
    elif sort_by == 'occupancy':
        spots_qs = spots_qs.order_by('-annotated_active_checkins', 'name')
    elif sort_by == 'name':
        spots_qs = spots_qs.order_by('name')
    else:
        spots_qs = spots_qs.order_by('-id')

    # Convert to list to apply Open Now if selected and collect meta
    spots_list = list(spots_qs)
    if open_now == '1':
        spots_list = [s for s in spots_list if s.is_open_now]

    # User saved spots
    saved_spot_ids = set()
    if current_user:
        saved_spot_ids = set(
            SavedSpot.objects.filter(user=current_user).values_list('spot_id', flat=True)
        )

    # Dashboard Quick Stats
    total_spots_count = StudySpot.objects.count()
    active_checkins_total = CheckIn.objects.filter(is_active=True).count()
    total_reviews_count = Review.objects.count()

    context = {
        'spots': spots_list,
        'saved_spot_ids': saved_spot_ids,
        'q': q,
        'category': category,
        'price_tier': price_tier,
        'outlet_density': outlet_density,
        'predominant_noise': predominant_noise,
        'min_wifi': min_wifi,
        'open_now': open_now,
        'match_prefs': match_prefs,
        'sort_by': sort_by,
        'total_spots_count': total_spots_count,
        'active_checkins_total': active_checkins_total,
        'total_reviews_count': total_reviews_count,
    }
    return render(request, "home/home.html", context)


@login_required
def toggle_save_spot_view(request, spot_id):
    user = get_logged_in_user(request)
    spot = get_object_or_404(StudySpot, id=spot_id)
    saved_obj = SavedSpot.objects.filter(user=user, spot=spot).first()

    if saved_obj:
        saved_obj.delete()
        is_saved = False
        message = f"Removed {spot.name} from your saved spots."
    else:
        SavedSpot.objects.create(user=user, spot=spot)
        is_saved = True
        message = f"Saved {spot.name} to your favorites!"

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'success': True,
            'is_saved': is_saved,
            'message': message,
            'total_saved': SavedSpot.objects.filter(user=user).count()
        })

    messages.success(request, message)
    next_url = request.META.get('HTTP_REFERER') or 'home:home'
    return redirect(next_url)


@login_required
def saved_spots_view(request):
    user = get_logged_in_user(request)
    saved_entries = SavedSpot.objects.filter(user=user).select_related('spot', 'spot__amenities').order_by('-saved_at')
    spots = [entry.spot for entry in saved_entries]
    saved_spot_ids = {entry.spot_id for entry in saved_entries}

    return render(request, "home/saved_spots.html", {
        'spots': spots,
        'saved_spot_ids': saved_spot_ids,
        'total_saved': len(spots),
    })


@login_required
def add_spot_view(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', 'CAFE').strip()
        address = request.POST.get('address', '').strip()
        latitude = request.POST.get('latitude', '10.315700').strip()
        longitude = request.POST.get('longitude', '123.885400').strip()
        opening_time = request.POST.get('opening_time', '').strip() or None
        closing_time = request.POST.get('closing_time', '').strip() or None
        price_tier = request.POST.get('price_tier', '₱₱').strip()

        wifi_speed = request.POST.get('wifi_speed', '50.0').strip()
        outlet_density = request.POST.get('outlet_density', 'PLENTIFUL').strip()
        predominant_noise = request.POST.get('predominant_noise', 'QUIET').strip()

        if not name or not address:
            messages.error(request, "Spot name and address are required.")
            return redirect('home:home')

        try:
            spot = StudySpot.objects.create(
                name=name,
                category=category,
                address=address,
                latitude=Decimal(latitude),
                longitude=Decimal(longitude),
                opening_time=opening_time,
                closing_time=closing_time,
                price_tier=price_tier,
            )

            SpotAmenity.objects.create(
                spot=spot,
                avg_wifi_speed_mbps=Decimal(wifi_speed) if wifi_speed else Decimal("0.0"),
                outlet_density=outlet_density,
                predominant_noise=predominant_noise,
                last_recalculated_at=timezone.now(),
            )

            messages.success(request, f"Study spot '{spot.name}' added successfully!")
            return redirect('home:home')
        except Exception as e:
            messages.error(request, f"Error adding spot: {str(e)}")
            return redirect('home:home')

    return redirect('home:home')
