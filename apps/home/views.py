from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg, Count, Subquery, F
from django.utils import timezone
from apps.home.models import User, StudySpot, SpotAmenity, Review, CheckIn, SavedSpot
from apps.login.auth_helper import login_required, get_logged_in_user
from apps.home.services import (
    execute_user_checkin,
    execute_recalculate_amenities,
    get_top_rated_spots_from_view,
    get_late_night_hubs_from_view,
    get_spot_amenity_summary_from_view,
)


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
        except (InvalidOperation, ValueError, TypeError):
            pass

    # Open Now filter (database-level schedule check supporting overnight hours)
    if open_now == '1':
        now = timezone.localtime().time()
        spots_qs = spots_qs.filter(
            Q(opening_time__isnull=True)
            | Q(closing_time__isnull=True)
            | (Q(opening_time__lte=F('closing_time')) & Q(opening_time__lte=now, closing_time__gte=now))
            | (Q(opening_time__gt=F('closing_time')) & (Q(opening_time__lte=now) | Q(closing_time__gte=now)))
        )

    # Annotate with rating and active check-ins count for sorting
    spots_qs = spots_qs.annotate(
        annotated_avg_rating=Avg('reviews__overall_rating'),
        annotated_review_count=Count('reviews', distinct=True),
        annotated_active_checkins=Count('check_ins__user_id', filter=Q(check_ins__is_active=True), distinct=True)
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

    # Analytical SQL Views data
    top_rated_spots = get_top_rated_spots_from_view(3)
    late_night_hubs = get_late_night_hubs_from_view(3)
    amenity_summary = get_spot_amenity_summary_from_view(5)

    context = {
        'spots': spots_qs,
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
        'top_rated_spots': top_rated_spots,
        'late_night_hubs': late_night_hubs,
        'amenity_summary': amenity_summary,
    }
    return render(request, "home/home.html", context)


def spot_detail_view(request, spot_id):
    spot = get_object_or_404(StudySpot.objects.select_related('amenities'), id=spot_id)
    current_user = get_logged_in_user(request)

    # Reviews ordered by newest first
    reviews = Review.objects.filter(spot=spot).select_related('user').order_by('-id')

    # Active check-ins at this spot (deduplicated per student user at DB level)
    active_checkins = (
        spot.check_ins.filter(is_active=True)
        .select_related('user')
        .order_by('user_id', '-checked_in_at')
        .distinct('user_id')
    )

    # Check if current user is saved or checked in
    is_saved = False
    is_user_checked_in_here = False
    user_active_checkin_elsewhere = None
    user_review = None

    if current_user:
        is_saved = SavedSpot.objects.filter(user=current_user, spot=spot).exists()
        active_ci = CheckIn.objects.filter(user=current_user, is_active=True).select_related('spot').first()
        if active_ci:
            if active_ci.spot_id == spot.id:
                is_user_checked_in_here = True
            else:
                user_active_checkin_elsewhere = active_ci
        user_review = Review.objects.filter(spot=spot, user=current_user).first()

    context = {
        'spot': spot,
        'reviews': reviews,
        'active_checkins': active_checkins,
        'is_saved': is_saved,
        'is_user_checked_in_here': is_user_checked_in_here,
        'user_active_checkin_elsewhere': user_active_checkin_elsewhere,
        'user_review': user_review,
    }
    return render(request, "home/spot_detail.html", context)


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
            lat_val = Decimal(latitude)
            lng_val = Decimal(longitude)
            wifi_val = Decimal(wifi_speed) if wifi_speed else Decimal("0.0")
        except (InvalidOperation, ValueError, TypeError):
            messages.error(
                request,
                "Invalid coordinates or numeric input: please enter valid decimal latitude, longitude, and Wi-Fi speed values.",
            )
            return redirect('home:home')

        spot = StudySpot.objects.create(
            name=name,
            category=category,
            address=address,
            latitude=lat_val,
            longitude=lng_val,
            opening_time=opening_time,
            closing_time=closing_time,
            price_tier=price_tier,
        )

        SpotAmenity.objects.create(
            spot=spot,
            avg_wifi_speed_mbps=wifi_val,
            outlet_density=outlet_density,
            predominant_noise=predominant_noise,
            last_recalculated_at=timezone.now(),
        )

        messages.success(request, f"Study spot '{spot.name}' added successfully!")
        return redirect('home:spot_detail', spot_id=spot.id)

    return redirect('home:home')


@login_required
def toggle_checkin_view(request, spot_id):
    user = get_logged_in_user(request)
    spot = get_object_or_404(StudySpot, id=spot_id)

    # Check if user is currently checked into THIS spot
    current_checkin = CheckIn.objects.filter(user=user, spot=spot, is_active=True).first()

    if current_checkin:
        # Check out
        current_checkin.is_active = False
        current_checkin.save()
        messages.info(request, f"You have checked out of {spot.name}.")
    else:
        # Check into this spot (using stored procedure or service)
        execute_user_checkin(user.id, spot.id)
        messages.success(request, f"Checked in to {spot.name}! Your study session is now active.")

    return redirect('home:spot_detail', spot_id=spot.id)


@login_required
def add_review_view(request, spot_id):
    user = get_logged_in_user(request)
    spot = get_object_or_404(StudySpot, id=spot_id)

    if request.method == "POST":
        overall_rating = int(request.POST.get('overall_rating', 5))
        outlet_rating = request.POST.get('outlet_rating', 'PLENTIFUL').strip()
        noise_level = request.POST.get('noise_level', 'QUIET').strip()
        download_speed = request.POST.get('download_speed_mbps', '').strip()
        upload_speed = request.POST.get('upload_speed_mbps', '').strip()
        review_text = request.POST.get('review_text', '').strip()

        download_val = Decimal(download_speed) if download_speed else None
        upload_val = Decimal(upload_speed) if upload_speed else None

        Review.objects.update_or_create(
            spot=spot,
            user=user,
            defaults={
                'overall_rating': overall_rating,
                'outlet_rating': outlet_rating,
                'noise_level': noise_level,
                'download_speed_mbps': download_val,
                'upload_speed_mbps': upload_val,
                'review_text': review_text,
            }
        )

        # Recalculate amenities for this spot
        execute_recalculate_amenities(spot.id)

        messages.success(request, f"Thank you! Your speed-test and review for {spot.name} have been submitted.")

    return redirect('home:spot_detail', spot_id=spot.id)


@login_required
def delete_review_view(request, review_id):
    user = get_logged_in_user(request)
    review = get_object_or_404(Review, id=review_id, user=user)
    spot_id = review.spot_id
    spot_name = review.spot.name
    review.delete()

    # Recalculate amenities
    execute_recalculate_amenities(spot_id)

    messages.info(request, f"Your review for {spot_name} has been deleted.")
    return redirect('home:spot_detail', spot_id=spot_id)


def sql_insights(request):
    """
    CSIT327 Lab Activity: SQL JOINS and SUBQUERIES using Django ORM and Supabase PostgreSQL.
    Demonstrates:
    1. SQL JOIN: Review.objects.select_related('user', 'spot')
    2. SQL SUBQUERY: StudySpot.objects.filter(id__in=Subquery(...))
    """
    # SQL JOIN (select_related)
    reviews_joined = Review.objects.select_related('user', 'spot').all().order_by('-id')
    join_sql = str(reviews_joined.query)

    # SQL SUBQUERY (Subquery)
    overall_avg = SpotAmenity.objects.aggregate(overall_avg=Avg('avg_wifi_speed_mbps'))['overall_avg']
    if overall_avg is None:
        avg_wifi = 0
        high_speed_spots = StudySpot.objects.none()
        subquery_sql = ""
    else:
        avg_wifi = overall_avg
        high_speed_spot_ids = SpotAmenity.objects.filter(
            avg_wifi_speed_mbps__gte=avg_wifi
        ).values('spot_id')

        high_speed_spots = StudySpot.objects.filter(
            id__in=Subquery(high_speed_spot_ids)
        ).order_by('id')
        subquery_sql = str(high_speed_spots.query)

    context = {
        'reviews_joined': reviews_joined,
        'join_sql': join_sql,
        'high_speed_spots': high_speed_spots,
        'avg_wifi': round(float(avg_wifi), 2),
        'subquery_sql': subquery_sql,
    }
    return render(request, 'home/insights.html', context)

