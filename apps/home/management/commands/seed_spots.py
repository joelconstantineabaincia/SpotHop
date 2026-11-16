import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from apps.home.models import User, StudySpot, SpotAmenity, Review, CheckIn, SavedSpot

class Command(BaseCommand):
    help = "Seed rich, realistic dataset for SpotHop (Cebu university study spots, users, reviews, check-ins)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write("Cleaning existing records...")
            SavedSpot.objects.all().delete()
            CheckIn.objects.all().delete()
            Review.objects.all().delete()
            SpotAmenity.objects.all().delete()
            StudySpot.objects.all().delete()
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing records cleaned."))

        self.stdout.write("Seeding Users...")
        default_pwd = make_password("password123")

        users_data = [
            {
                "username": "demo_user",
                "email": "demo@spothop.ph",
                "password_hash": default_pwd,
                "full_name": "Demo Student",
                "bio": "CSIT Senior student studying at USC Talamban. Passionate about quiet study cafés with high-speed Wi-Fi.",
                "preferred_noise_level": "QUIET",
                "preferred_outlet_density": "PLENTIFUL",
                "min_wifi_speed_mbps": Decimal("40.00"),
                "dark_mode": False,
                "email_notifications": True,
            },
            {
                "username": "juan_cruz",
                "email": "juan.cruz@cit.edu.ph",
                "password_hash": default_pwd,
                "full_name": "Juan Dela Cruz",
                "bio": "CIT-U Engineering student. Night owl looking for 24/7 or late-night study hubs.",
                "preferred_noise_level": "MODERATE",
                "preferred_outlet_density": "PLENTIFUL",
                "min_wifi_speed_mbps": Decimal("30.00"),
                "dark_mode": True,
                "email_notifications": True,
            },
            {
                "username": "maria_santos",
                "email": "maria.santos@up.edu.ph",
                "password_hash": default_pwd,
                "full_name": "Maria Santos",
                "bio": "UP Cebu Biology major. Prefers silent library corners and cozy aesthetic cafés.",
                "preferred_noise_level": "SILENT",
                "preferred_outlet_density": "SCARCE",
                "min_wifi_speed_mbps": Decimal("25.00"),
                "dark_mode": False,
                "email_notifications": False,
            },
            {
                "username": "kiko_reyes",
                "email": "kiko.reyes@usc.edu.ph",
                "password_hash": default_pwd,
                "full_name": "Francis 'Kiko' Reyes",
                "bio": "Tech enthusiast and software intern at IT Park. Always hunting for power outlets and fast uploads.",
                "preferred_noise_level": "QUIET",
                "preferred_outlet_density": "PLENTIFUL",
                "min_wifi_speed_mbps": Decimal("50.00"),
                "dark_mode": True,
                "email_notifications": True,
            },
            {
                "username": "sophia_lim",
                "email": "sophia.lim@velez.edu.ph",
                "password_hash": default_pwd,
                "full_name": "Sophia Lim",
                "bio": "Velez College Medical Technology student. Needs absolute silence during board review season.",
                "preferred_noise_level": "SILENT",
                "preferred_outlet_density": "PLENTIFUL",
                "min_wifi_speed_mbps": Decimal("20.00"),
                "dark_mode": False,
                "email_notifications": True,
            },
            {
                "username": "carlo_tan",
                "email": "carlo.tan@cdu.edu.ph",
                "password_hash": default_pwd,
                "full_name": "Carlo Tan",
                "bio": "CDU PT student. Group study leader and specialty coffee lover.",
                "preferred_noise_level": "MODERATE",
                "preferred_outlet_density": "PLENTIFUL",
                "min_wifi_speed_mbps": Decimal("35.00"),
                "dark_mode": False,
                "email_notifications": True,
            },
        ]

        user_instances = {}
        for udata in users_data:
            user, created = User.objects.update_or_create(
                username=udata["username"],
                defaults=udata
            )
            user_instances[udata["username"]] = user

        self.stdout.write(f"Seeded {len(user_instances)} users.")

        self.stdout.write("Seeding Study Spots & Amenities...")
        spots_data = [
            {
                "name": "The Coffee Code - IT Park",
                "category": "CAFE",
                "address": "Skyrise 4, IT Park, Lahug, Cebu City",
                "latitude": Decimal("10.329800"),
                "longitude": Decimal("123.906400"),
                "opening_time": datetime.time(7, 0),
                "closing_time": datetime.time(2, 0),  # Late night (02:00 AM)
                "price_tier": "₱₱",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("95.50"),
                    "outlet_density": "PLENTIFUL",
                    "predominant_noise": "QUIET",
                }
            },
            {
                "name": "USC Knowledge Commons (Talamban)",
                "category": "LIBRARY",
                "address": "Josef Baumgartner Learning Resource Center, USC Talamban Campus, Cebu City",
                "latitude": Decimal("10.354200"),
                "longitude": Decimal("123.914200"),
                "opening_time": datetime.time(8, 0),
                "closing_time": datetime.time(20, 0),
                "price_tier": "FREE",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("120.00"),
                    "outlet_density": "PLENTIFUL",
                    "predominant_noise": "SILENT",
                }
            },
            {
                "name": "Tightrope Coffee - F. Ramos",
                "category": "CAFE",
                "address": "9 President M. Quezon St, F. Ramos, Cebu City",
                "latitude": Decimal("10.311700"),
                "longitude": Decimal("123.898800"),
                "opening_time": datetime.time(7, 0),
                "closing_time": datetime.time(23, 0),  # Late night (23:00)
                "price_tier": "₱₱",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("82.00"),
                    "outlet_density": "PLENTIFUL",
                    "predominant_noise": "MODERATE",
                }
            },
            {
                "name": "The Company Cebu - IT Park Hub",
                "category": "COWORKING",
                "address": "15th Floor, HM Tower, Geonzon St, Cebu IT Park",
                "latitude": Decimal("10.330400"),
                "longitude": Decimal("123.906800"),
                "opening_time": datetime.time(8, 0),
                "closing_time": datetime.time(23, 59),  # Open until midnight / late night
                "price_tier": "₱₱₱",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("150.00"),
                    "outlet_density": "PLENTIFUL",
                    "predominant_noise": "QUIET",
                }
            },
            {
                "name": "Bintana Coffee House",
                "category": "CAFE",
                "address": "Elizabeth Pond St, Kamputhaw, Cebu City",
                "latitude": Decimal("10.318200"),
                "longitude": Decimal("123.896100"),
                "opening_time": datetime.time(9, 0),
                "closing_time": datetime.time(22, 0),
                "price_tier": "₱",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("42.00"),
                    "outlet_density": "SCARCE",
                    "predominant_noise": "QUIET",
                }
            },
            {
                "name": "UP Cebu Student Commons & Library",
                "category": "LOUNGE",
                "address": "Gorordo Ave, Lahug, Cebu City",
                "latitude": Decimal("10.322800"),
                "longitude": Decimal("123.898900"),
                "opening_time": datetime.time(8, 0),
                "closing_time": datetime.time(21, 0),
                "price_tier": "FREE",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("65.00"),
                    "outlet_density": "PLENTIFUL",
                    "predominant_noise": "QUIET",
                }
            },
            {
                "name": "Workplace Café - Banawa Branch",
                "category": "COWORKING",
                "address": "Autogas Station Complex, Duterte St, Banawa, Cebu City",
                "latitude": Decimal("10.316800"),
                "longitude": Decimal("123.882400"),
                "opening_time": datetime.time(6, 0),
                "closing_time": datetime.time(23, 59),  # 24hr / late night
                "price_tier": "₱₱",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("110.00"),
                    "outlet_density": "PLENTIFUL",
                    "predominant_noise": "QUIET",
                }
            },
            {
                "name": "Nomad's Hub - Ramos",
                "category": "COWORKING",
                "address": "Building F, Ramos St, Barangay Cogon Ramos, Cebu City",
                "latitude": Decimal("10.309800"),
                "longitude": Decimal("123.897200"),
                "opening_time": datetime.time(8, 0),
                "closing_time": datetime.time(2, 0),  # Late night (02:00 AM)
                "price_tier": "₱₱",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("88.00"),
                    "outlet_density": "PLENTIFUL",
                    "predominant_noise": "QUIET",
                }
            },
            {
                "name": "Cebu City Public Library",
                "category": "LIBRARY",
                "address": "Rizal Memorial Library & Museum Bldg, Osmeña Blvd, Cebu City",
                "latitude": Decimal("10.308200"),
                "longitude": Decimal("123.893100"),
                "opening_time": datetime.time(8, 0),
                "closing_time": datetime.time(23, 0),  # Late night (23:00)
                "price_tier": "FREE",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("45.00"),
                    "outlet_density": "SCARCE",
                    "predominant_noise": "SILENT",
                }
            },
            {
                "name": "Good Cup Coffee Co.",
                "category": "CAFE",
                "address": "F. Ramos St, Cogon Ramos, Cebu City",
                "latitude": Decimal("10.310500"),
                "longitude": Decimal("123.899200"),
                "opening_time": datetime.time(7, 30),
                "closing_time": datetime.time(19, 0),
                "price_tier": "₱₱",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("68.00"),
                    "outlet_density": "PLENTIFUL",
                    "predominant_noise": "MODERATE",
                }
            },
            {
                "name": "Avenir Coworking Lab",
                "category": "COWORKING",
                "address": "Avenir Building, Archbishop Reyes Ave, Lahug, Cebu City",
                "latitude": Decimal("10.324500"),
                "longitude": Decimal("123.903200"),
                "opening_time": datetime.time(7, 0),
                "closing_time": datetime.time(23, 30),  # Late night (23:30)
                "price_tier": "₱₱",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("135.00"),
                    "outlet_density": "PLENTIFUL",
                    "predominant_noise": "QUIET",
                }
            },
            {
                "name": "Linear Coffee Roasters",
                "category": "CAFE",
                "address": "Parkmall / Big Hotel Complex, Mandaue City, Cebu",
                "latitude": Decimal("10.323500"),
                "longitude": Decimal("123.931800"),
                "opening_time": datetime.time(8, 0),
                "closing_time": datetime.time(21, 0),
                "price_tier": "₱₱",
                "amenity": {
                    "avg_wifi_speed_mbps": Decimal("52.00"),
                    "outlet_density": "SCARCE",
                    "predominant_noise": "MODERATE",
                }
            },
        ]

        spot_instances = {}
        for sdata in spots_data:
            amenity_info = sdata.pop("amenity")
            spot, created = StudySpot.objects.update_or_create(
                name=sdata["name"],
                defaults=sdata
            )
            spot_instances[sdata["name"]] = spot

            SpotAmenity.objects.update_or_create(
                spot=spot,
                defaults={
                    "avg_wifi_speed_mbps": amenity_info["avg_wifi_speed_mbps"],
                    "outlet_density": amenity_info["outlet_density"],
                    "predominant_noise": amenity_info["predominant_noise"],
                    "last_recalculated_at": timezone.now(),
                }
            )

        self.stdout.write(f"Seeded {len(spot_instances)} study spots with amenities.")

        self.stdout.write("Seeding Reviews...")
        reviews_data = [
            # The Coffee Code
            {
                "spot_name": "The Coffee Code - IT Park",
                "username": "kiko_reyes",
                "overall_rating": 5,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "QUIET",
                "download_speed_mbps": Decimal("98.40"),
                "upload_speed_mbps": Decimal("48.20"),
                "review_text": "One of my absolute favorite spots in IT Park. Sockets under almost every table and great cold brew!",
            },
            {
                "spot_name": "The Coffee Code - IT Park",
                "username": "demo_user",
                "overall_rating": 4,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "QUIET",
                "download_speed_mbps": Decimal("92.60"),
                "upload_speed_mbps": Decimal("40.10"),
                "review_text": "Super reliable Wi-Fi for coding and Zoom calls. Gets a bit full around 4 PM but turnover is fast.",
            },
            {
                "spot_name": "The Coffee Code - IT Park",
                "username": "juan_cruz",
                "overall_rating": 5,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "QUIET",
                "download_speed_mbps": Decimal("96.00"),
                "upload_speed_mbps": Decimal("45.00"),
                "review_text": "Open until 2 AM! Lifesaver for midterms and thesis crunch time.",
            },
            # USC Knowledge Commons
            {
                "spot_name": "USC Knowledge Commons (Talamban)",
                "username": "demo_user",
                "overall_rating": 5,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "SILENT",
                "download_speed_mbps": Decimal("125.50"),
                "upload_speed_mbps": Decimal("85.00"),
                "review_text": "World-class university library. Fiber Wi-Fi is blazingly fast and ergonomic chairs are great.",
            },
            {
                "spot_name": "USC Knowledge Commons (Talamban)",
                "username": "sophia_lim",
                "overall_rating": 5,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "SILENT",
                "download_speed_mbps": Decimal("118.00"),
                "upload_speed_mbps": Decimal("80.00"),
                "review_text": "Complete silence, aircon is cold, and plenty of power outlets on every floor.",
            },
            # Tightrope Coffee
            {
                "spot_name": "Tightrope Coffee - F. Ramos",
                "username": "carlo_tan",
                "overall_rating": 4,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "MODERATE",
                "download_speed_mbps": Decimal("85.00"),
                "upload_speed_mbps": Decimal("30.00"),
                "review_text": "Aesthetic minimalist café with superb espresso. Great for reading and light laptop work.",
            },
            {
                "spot_name": "Tightrope Coffee - F. Ramos",
                "username": "maria_santos",
                "overall_rating": 4,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "MODERATE",
                "download_speed_mbps": Decimal("79.00"),
                "upload_speed_mbps": Decimal("28.00"),
                "review_text": "Very cozy vibe. Gets moderately lively in the afternoon but headphone noise cancellation handles it.",
            },
            # The Company Cebu
            {
                "spot_name": "The Company Cebu - IT Park Hub",
                "username": "kiko_reyes",
                "overall_rating": 5,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "QUIET",
                "download_speed_mbps": Decimal("155.00"),
                "upload_speed_mbps": Decimal("95.00"),
                "review_text": "Unmatched workspace amenities. Unlimited brew coffee and enterprise fiber network.",
            },
            {
                "spot_name": "The Company Cebu - IT Park Hub",
                "username": "juan_cruz",
                "overall_rating": 5,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "QUIET",
                "download_speed_mbps": Decimal("145.00"),
                "upload_speed_mbps": Decimal("90.00"),
                "review_text": "Best place for hackathons and group project submissions. Open late!",
            },
            # Workplace Café Banawa
            {
                "spot_name": "Workplace Café - Banawa Branch",
                "username": "juan_cruz",
                "overall_rating": 5,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "QUIET",
                "download_speed_mbps": Decimal("112.00"),
                "upload_speed_mbps": Decimal("60.00"),
                "review_text": "Late night haven for college students. Power cubicles, nap zone, and affordable iced coffee.",
            },
            {
                "spot_name": "Workplace Café - Banawa Branch",
                "username": "demo_user",
                "overall_rating": 5,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "QUIET",
                "download_speed_mbps": Decimal("108.00"),
                "upload_speed_mbps": Decimal("58.00"),
                "review_text": "Super productive atmosphere. Everyone here is dialed into studying or remote work.",
            },
            # Nomad's Hub
            {
                "spot_name": "Nomad's Hub - Ramos",
                "username": "maria_santos",
                "overall_rating": 4,
                "outlet_rating": "PLENTIFUL",
                "noise_level": "QUIET",
                "download_speed_mbps": Decimal("90.00"),
                "upload_speed_mbps": Decimal("40.00"),
                "review_text": "Quiet coworking and hostel space near Velez and Ramos. Open until 2 AM.",
            },
            # Cebu City Public Library
            {
                "spot_name": "Cebu City Public Library",
                "username": "sophia_lim",
                "overall_rating": 4,
                "outlet_rating": "SCARCE",
                "noise_level": "SILENT",
                "download_speed_mbps": Decimal("45.00"),
                "upload_speed_mbps": Decimal("15.00"),
                "review_text": "Historic public library, open until 11 PM. Perfect for quiet reading, bring a fully charged laptop or power bank.",
            },
        ]

        review_count = 0
        for rdata in reviews_data:
            spot = spot_instances.get(rdata["spot_name"])
            user = user_instances.get(rdata["username"])
            if spot and user:
                review, created = Review.objects.update_or_create(
                    spot=spot,
                    user=user,
                    defaults={
                        "overall_rating": rdata["overall_rating"],
                        "outlet_rating": rdata["outlet_rating"],
                        "noise_level": rdata["noise_level"],
                        "download_speed_mbps": rdata["download_speed_mbps"],
                        "upload_speed_mbps": rdata["upload_speed_mbps"],
                        "review_text": rdata["review_text"],
                    }
                )
                review_count += 1

        self.stdout.write(f"Seeded {review_count} crowd-sourced reviews.")

        self.stdout.write("Seeding Check-Ins...")
        # Active and past check-ins
        check_ins_data = [
            {"username": "demo_user", "spot_name": "The Coffee Code - IT Park", "is_active": True, "mins_ago": 25},
            {"username": "kiko_reyes", "spot_name": "The Coffee Code - IT Park", "is_active": True, "mins_ago": 45},
            {"username": "maria_santos", "spot_name": "USC Knowledge Commons (Talamban)", "is_active": True, "mins_ago": 15},
            {"username": "sophia_lim", "spot_name": "USC Knowledge Commons (Talamban)", "is_active": True, "mins_ago": 80},
            {"username": "juan_cruz", "spot_name": "Workplace Café - Banawa Branch", "is_active": True, "mins_ago": 30},
            {"username": "carlo_tan", "spot_name": "Tightrope Coffee - F. Ramos", "is_active": True, "mins_ago": 60},
            # Past check ins
            {"username": "demo_user", "spot_name": "USC Knowledge Commons (Talamban)", "is_active": False, "mins_ago": 240},
            {"username": "kiko_reyes", "spot_name": "The Company Cebu - IT Park Hub", "is_active": False, "mins_ago": 360},
            {"username": "juan_cruz", "spot_name": "Nomad's Hub - Ramos", "is_active": False, "mins_ago": 480},
        ]

        checkin_count = 0
        now = timezone.now()
        for cdata in check_ins_data:
            spot = spot_instances.get(cdata["spot_name"])
            user = user_instances.get(cdata["username"])
            if spot and user:
                CheckIn.objects.create(
                    user=user,
                    spot=spot,
                    checked_in_at=now - datetime.timedelta(minutes=cdata["mins_ago"]),
                    is_active=cdata["is_active"]
                )
                checkin_count += 1

        self.stdout.write(f"Seeded {checkin_count} check-ins.")

        self.stdout.write("Seeding Saved Spots (Bookmarks)...")
        saved_spots_data = [
            ("demo_user", "The Coffee Code - IT Park"),
            ("demo_user", "USC Knowledge Commons (Talamban)"),
            ("demo_user", "The Company Cebu - IT Park Hub"),
            ("juan_cruz", "Workplace Café - Banawa Branch"),
            ("juan_cruz", "Nomad's Hub - Ramos"),
            ("maria_santos", "USC Knowledge Commons (Talamban)"),
            ("maria_santos", "Bintana Coffee House"),
            ("kiko_reyes", "The Company Cebu - IT Park Hub"),
            ("kiko_reyes", "Avenir Coworking Lab"),
            ("sophia_lim", "Cebu City Public Library"),
            ("sophia_lim", "USC Knowledge Commons (Talamban)"),
        ]

        saved_count = 0
        for uname, sname in saved_spots_data:
            user = user_instances.get(uname)
            spot = spot_instances.get(sname)
            if user and spot:
                SavedSpot.objects.get_or_create(
                    user=user,
                    spot=spot,
                    defaults={"saved_at": now - datetime.timedelta(hours=saved_count + 1)}
                )
                saved_count += 1

        self.stdout.write(f"Seeded {saved_count} saved spots.")
        self.stdout.write(self.style.SUCCESS("SpotHop realistic dataset successfully seeded!"))
