# SpotHop 🎓☕

> **CSIT327 Final Project — University Study Spot & Work Café Finder**
> Production-ready Django web application connected to Supabase PostgreSQL, designed to help students discover and log productive study spaces based on real Wi-Fi speeds, power outlet availability, ambient noise, price tier, and live peer occupancy.

---

## 🌟 Key Features

1. **Package-by-Feature (Vertical Slicing) Architecture:**
   - `apps/login/`: User authentication, session management, secure password validation.
   - `apps/register/`: Account creation with PBKDF2/SHA256 password hashing.
   - `apps/home/`: Approved Physical ERD models, study spot directory, multi-parameter filtering, bookmarking, and spot creation.
   - `apps/user_profile/`: Student profile overview, editable bio, check-in history, and review activity.
   - `apps/user_settings/`: Study preferences configuration (`preferred_noise_level`, `preferred_outlet_density`, `min_wifi_speed_mbps`), notifications, and full-application **Dark Mode**.

2. **Multi-Parameter Search & Filtering:**
   - Search by spot name, address, or campus neighborhood.
   - Filter by category (Café, Library, Co-working, Campus Lounge), price tier (`FREE`, `₱`, `₱₱`, `₱₱₱`), outlet density, noise level, and minimum Wi-Fi speed threshold.
   - **"Open Now" Toggle:** Automatically calculates real-time operating hours, including past-midnight / 24-hr study hubs.
   - **"Match My Preferences" Mode:** Instantly tailors the directory to the logged-in student's saved noise, outlet, and Wi-Fi criteria.

3. **Live Presence Check-In System:**
   - One-click Check In / Check Out toggle for study spaces.
   - Automatic single-active-session enforcement (checking into a new spot deactivates previous active check-ins).
   - Real-time student occupancy counter on every spot card.

4. **Crowd-Sourced Reviews & Wi-Fi Speed-Test Logger:**
   - Log verified download and upload speeds (Mbps), 1–5 star ratings, outlet abundance, and study environment tips.
   - Full CRUD capability (submit, edit, delete reviews).

5. **PostgreSQL Stored Procedures & Analytical Views:**
   - **Stored Procedure `log_user_checkin(p_user_id, p_spot_id)`**: Handles atomic check-in transitions in PostgreSQL.
   - **Stored Procedure `recalculate_spot_amenities(p_spot_id)`**: Recomputes average Wi-Fi speeds and dominant outlet/noise modes on review updates.
   - **SQL View `vw_top_rated_spots`**: Aggregates top-rated spots and review volume.
   - **SQL View `vw_late_night_study_hubs`**: Surfaces spots open past 22:00 with verified Wi-Fi > 30 Mbps.
   - **SQL View `vw_spot_amenity_summary`**: Summarizes verified amenities and live active student counts.

6. **Responsive UI & Dark Mode:**
   - Built on modern Bootstrap 5.3 with Bootstrap Icons.
   - High-contrast, accessibility-focused Dark Mode toggle persisted to user settings and localStorage.

---

## 🏗️ Architecture & Approved Physical ERD

```
spothop_project/
├── apps/
│   ├── home/                  # Core ERD Models, Directory, Reviews, Check-Ins, Services
│   │   ├── migrations/        # 0001_initial, 0002_stored_procedures_and_views
│   │   ├── management/        # seed_spots command
│   │   ├── models.py          # Users, StudySpots, SpotAmenities, Reviews, CheckIns, SavedSpots
│   │   ├── services.py        # Stored procedure & SQL view executors
│   │   ├── urls.py
│   │   └── views.py
│   ├── login/                 # Login & Logout Vertical Slice
│   ├── register/              # User Registration Slice
│   ├── user_profile/          # Profile & Study History Slice
│   └── user_settings/         # Settings & Dark Mode Slice
├── myproject/                 # Django core config (settings, wsgi, asgi, urls)
├── static/                    # CSS, JS, and image assets per feature
├── templates/                 # base.html, home/, login/, register/, user_profile/, user_settings/
├── requirements.txt           # Production dependencies (Django, psycopg, gunicorn, whitenoise)
└── manage.py
```

### Approved Physical ERD (6 Relational Tables):
1. `users` (`User`)
2. `study_spots` (`StudySpot`)
3. `spot_amenities` (`SpotAmenity` — 1:1 with `StudySpot`)
4. `reviews` (`Review` — 1:M from `User` & `StudySpot`)
5. `check_ins` (`CheckIn` — 1:M from `User` & `StudySpot`)
6. `saved_spots` (`SavedSpot` — Junction table with unique constraint on `(user, spot)`)

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- PostgreSQL (or Supabase project)

### 2. Environment Setup
Configure `.env` in the project root:
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres?sslmode=require
```

### 3. Installation
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Database Migrations & Seeding
```bash
python manage.py migrate
python manage.py seed_spots
```

### 5. Run Server
```bash
python manage.py runserver 8080
```
Visit `http://127.0.0.1:8080/` in your browser.

**Demo Account:**
- Username: `demo_user`
- Password: `password123`

---

## ☁️ Production Deployment Readiness

- **WSGI Server:** `gunicorn` configured in `requirements.txt`.
- **Static Assets:** `whitenoise` middleware and `CompressedManifestStaticFilesStorage` enabled.
- **Port:** Configured to bind on port `8080`.
- **Database:** Fully pooled PostgreSQL via Supabase with SSL enforcement.
