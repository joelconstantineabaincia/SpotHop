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

        # Average download speed
        speeds = [r.download_speed_mbps for r in reviews if r.download_speed_mbps is not None]
        avg_speed = sum(speeds) / len(speeds) if speeds else None

        # Mode outlet rating
        outlets = [r.outlet_rating for r in reviews if r.outlet_rating]
        predominant_outlet = Counter(outlets).most_common(1)[0][0] if outlets else 'PLENTIFUL'

        # Mode noise level
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
