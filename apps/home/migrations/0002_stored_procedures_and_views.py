from django.db import migrations

CREATE_PROCEDURE_LOG_CHECKIN = """
CREATE OR REPLACE PROCEDURE log_user_checkin(p_user_id BIGINT, p_spot_id BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Deactivate all currently active check-ins for the user
    UPDATE check_ins
    SET is_active = FALSE
    WHERE user_id = p_user_id AND is_active = TRUE;

    -- Insert new active check-in
    INSERT INTO check_ins (user_id, spot_id, checked_in_at, is_active)
    VALUES (p_user_id, p_spot_id, NOW(), TRUE);
END;
$$;
"""

DROP_PROCEDURE_LOG_CHECKIN = """
DROP PROCEDURE IF EXISTS log_user_checkin(BIGINT, BIGINT);
"""

CREATE_PROCEDURE_RECALCULATE = """
CREATE OR REPLACE PROCEDURE recalculate_spot_amenities(p_spot_id BIGINT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_avg_wifi NUMERIC(6, 2);
    v_mode_outlet VARCHAR(20);
    v_mode_noise VARCHAR(20);
BEGIN
    -- Compute average download speed for this spot
    SELECT ROUND(AVG(download_speed_mbps), 2)
    INTO v_avg_wifi
    FROM reviews
    WHERE spot_id = p_spot_id AND download_speed_mbps IS NOT NULL;

    -- Compute mode/dominant outlet rating
    SELECT outlet_rating
    INTO v_mode_outlet
    FROM reviews
    WHERE spot_id = p_spot_id AND outlet_rating IS NOT NULL
    GROUP BY outlet_rating
    ORDER BY COUNT(*) DESC, outlet_rating ASC
    LIMIT 1;

    -- Compute mode/dominant noise level
    SELECT noise_level
    INTO v_mode_noise
    FROM reviews
    WHERE spot_id = p_spot_id AND noise_level IS NOT NULL
    GROUP BY noise_level
    ORDER BY COUNT(*) DESC, noise_level ASC
    LIMIT 1;

    -- Upsert spot_amenities record
    INSERT INTO spot_amenities (spot_id, avg_wifi_speed_mbps, outlet_density, predominant_noise, last_recalculated_at)
    VALUES (
        p_spot_id,
        COALESCE(v_avg_wifi, 0.00),
        COALESCE(v_mode_outlet, 'PLENTIFUL'),
        COALESCE(v_mode_noise, 'QUIET'),
        NOW()
    )
    ON CONFLICT (spot_id) DO UPDATE SET
        avg_wifi_speed_mbps = COALESCE(v_avg_wifi, spot_amenities.avg_wifi_speed_mbps),
        outlet_density = COALESCE(v_mode_outlet, spot_amenities.outlet_density),
        predominant_noise = COALESCE(v_mode_noise, spot_amenities.predominant_noise),
        last_recalculated_at = NOW();
END;
$$;
"""

DROP_PROCEDURE_RECALCULATE = """
DROP PROCEDURE IF EXISTS recalculate_spot_amenities(BIGINT);
"""

CREATE_VIEW_TOP_RATED = """
CREATE OR REPLACE VIEW vw_top_rated_spots AS
SELECT 
    s.id AS spot_id,
    s.name,
    s.category,
    s.address,
    s.price_tier,
    COALESCE(ROUND(AVG(r.overall_rating), 1), 0.0) AS avg_rating,
    COUNT(r.id) AS review_count
FROM study_spots s
LEFT JOIN reviews r ON s.id = r.spot_id
GROUP BY s.id, s.name, s.category, s.address, s.price_tier
ORDER BY avg_rating DESC, review_count DESC;
"""

DROP_VIEW_TOP_RATED = """
DROP VIEW IF EXISTS vw_top_rated_spots;
"""

CREATE_VIEW_LATE_NIGHT = """
CREATE OR REPLACE VIEW vw_late_night_study_hubs AS
SELECT 
    s.id AS spot_id,
    s.name,
    s.category,
    s.address,
    s.opening_time,
    s.closing_time,
    s.price_tier,
    a.avg_wifi_speed_mbps,
    a.outlet_density,
    a.predominant_noise
FROM study_spots s
JOIN spot_amenities a ON s.id = a.spot_id
WHERE (
    (s.closing_time > '22:00:00')
    OR (s.closing_time <= '06:00:00' AND s.closing_time IS NOT NULL)
)
AND (a.avg_wifi_speed_mbps > 30.00)
ORDER BY a.avg_wifi_speed_mbps DESC;
"""

DROP_VIEW_LATE_NIGHT = """
DROP VIEW IF EXISTS vw_late_night_study_hubs;
"""

CREATE_VIEW_AMENITY_SUMMARY = """
CREATE OR REPLACE VIEW vw_spot_amenity_summary AS
SELECT 
    s.id AS spot_id,
    s.name,
    s.category,
    s.address,
    s.price_tier,
    s.opening_time,
    s.closing_time,
    COALESCE(a.avg_wifi_speed_mbps, 0.00) AS avg_wifi_speed_mbps,
    COALESCE(a.outlet_density, 'UNVERIFIED') AS outlet_density,
    COALESCE(a.predominant_noise, 'UNVERIFIED') AS predominant_noise,
    COALESCE(ci.active_checkins, 0) AS active_checkin_count
FROM study_spots s
LEFT JOIN spot_amenities a ON s.id = a.spot_id
LEFT JOIN (
    SELECT spot_id, COUNT(*) AS active_checkins
    FROM check_ins
    WHERE is_active = TRUE
    GROUP BY spot_id
) ci ON s.id = ci.spot_id
ORDER BY active_checkin_count DESC, s.name ASC;
"""

DROP_VIEW_AMENITY_SUMMARY = """
DROP VIEW IF EXISTS vw_spot_amenity_summary;
"""

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(CREATE_PROCEDURE_LOG_CHECKIN, reverse_sql=DROP_PROCEDURE_LOG_CHECKIN),
        migrations.RunSQL(CREATE_PROCEDURE_RECALCULATE, reverse_sql=DROP_PROCEDURE_RECALCULATE),
        migrations.RunSQL(CREATE_VIEW_TOP_RATED, reverse_sql=DROP_VIEW_TOP_RATED),
        migrations.RunSQL(CREATE_VIEW_LATE_NIGHT, reverse_sql=DROP_VIEW_LATE_NIGHT),
        migrations.RunSQL(CREATE_VIEW_AMENITY_SUMMARY, reverse_sql=DROP_VIEW_AMENITY_SUMMARY),
    ]
