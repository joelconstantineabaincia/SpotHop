from collections import Counter
from decimal import Decimal
from django.db import connection
from django.utils import timezone
from apps.home.models import StudySpot, SpotAmenity, Review, CheckIn

def execute_user_checkin(user_id, spot_id):
    """
    Executes a user check-in. Attempts to use stored procedure log_user_checkin,
    falling back to Django ORM if procedure is not yet created.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("CALL log_user_checkin(%s, %s);", [user_id, spot_id])
            return True
    except Exception:
        # Fallback to ORM
        CheckIn.objects.filter(user_id=user_id, is_active=True).update(is_active=False)
        CheckIn.objects.create(
            user_id=user_id,
            spot_id=spot_id,
            checked_in_at=timezone.now(),
            is_active=True
        )
        return True


def execute_recalculate_amenities(spot_id):
    """
    Recalculates spot amenities. Attempts to use stored procedure recalculate_spot_amenities,
    falling back to Django ORM aggregation if procedure is not yet created.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("CALL recalculate_spot_amenities(%s);", [spot_id])
            return True
    except Exception:
        # Fallback to ORM calculation
        reviews = Review.objects.filter(spot_id=spot_id)
        if not reviews.exists():
            return False

        speeds = [r.download_speed_mbps for r in reviews if r.download_speed_mbps is not None]
        avg_speed = sum(speeds) / len(speeds) if speeds else None

        outlets = [r.outlet_rating for r in reviews if r.outlet_rating]
        predominant_outlet = Counter(outlets).most_common(1)[0][0] if outlets else 'PLENTIFUL'

        noises = [r.noise_level for r in reviews if r.noise_level]
        predominant_noise = Counter(noises).most_common(1)[0][0] if noises else 'QUIET'

        SpotAmenity.objects.update_or_create(
            spot_id=spot_id,
            defaults={
                'avg_wifi_speed_mbps': round(Decimal(avg_speed), 2) if avg_speed is not None else None,
                'outlet_density': predominant_outlet,
                'predominant_noise': predominant_noise,
                'last_recalculated_at': timezone.now(),
            }
        )
        return True


def get_top_rated_spots_from_view(limit=3):
    """
    Fetches top-rated spots from SQL View vw_top_rated_spots.
    """
    results = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT spot_id, name, category, address, price_tier, avg_rating, review_count
                FROM vw_top_rated_spots
                WHERE review_count > 0
                ORDER BY avg_rating DESC, review_count DESC
                LIMIT %s;
            """, [limit])
            rows = cursor.fetchall()
            for r in rows:
                results.append({
                    'spot_id': r[0],
                    'name': r[1],
                    'category': r[2],
                    'address': r[3],
                    'price_tier': r[4],
                    'avg_rating': r[5],
                    'review_count': r[6],
                })
    except Exception as e:
        pass
    return results


def get_late_night_hubs_from_view(limit=3):
    """
    Fetches late-night study hubs from SQL View vw_late_night_study_hubs.
    """
    results = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT spot_id, name, category, address, opening_time, closing_time, price_tier, avg_wifi_speed_mbps, outlet_density, predominant_noise
                FROM vw_late_night_study_hubs
                ORDER BY avg_wifi_speed_mbps DESC
                LIMIT %s;
            """, [limit])
            rows = cursor.fetchall()
            for r in rows:
                results.append({
                    'spot_id': r[0],
                    'name': r[1],
                    'category': r[2],
                    'address': r[3],
                    'opening_time': r[4],
                    'closing_time': r[5],
                    'price_tier': r[6],
                    'avg_wifi_speed_mbps': r[7],
                    'outlet_density': r[8],
                    'predominant_noise': r[9],
                })
    except Exception as e:
        pass
    return results


def get_spot_amenity_summary_from_view(limit=5):
    """
    Fetches spot amenity & occupancy summary from SQL View vw_spot_amenity_summary.
    """
    results = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT spot_id, name, category, address, price_tier, opening_time, closing_time, avg_wifi_speed_mbps, outlet_density, predominant_noise, active_checkin_count
                FROM vw_spot_amenity_summary
                ORDER BY active_checkin_count DESC, avg_wifi_speed_mbps DESC
                LIMIT %s;
            """, [limit])
            rows = cursor.fetchall()
            for r in rows:
                results.append({
                    'spot_id': r[0],
                    'name': r[1],
                    'category': r[2],
                    'address': r[3],
                    'price_tier': r[4],
                    'opening_time': r[5],
                    'closing_time': r[6],
                    'avg_wifi_speed_mbps': r[7],
                    'outlet_density': r[8],
                    'predominant_noise': r[9],
                    'active_checkin_count': r[10],
                })
    except Exception as e:
        pass
    return results
