# NGO Volunteer Operations Platform – Validation & Functional Report

**Project root:** `/Users/soumyaranjanmohanty/Documents/NGO_DJANGO`

---

## ✅ Overall Validation
| Check | Result |
|-------|--------|
| Python syntax (`py_compile`) | **Pass** |
| Django system check (`manage.py check`) | **Pass** |
| Test suite (`manage.py test volunteers`) | **Pass – 4 tests** |
| Required dependencies installed (`requirements.txt`) | **Pass** |
| MongoDB driver (`pymongo`) available | **Pass** |

No syntax errors, no missing migrations, and all unit‑tests succeed.

---

## 📁 Folder Structure & Key Files
```
ngo_portal/                # Django project settings & URL config
│   __init__.py
│   asgi.py
│   settings.py          # added MONGO_URI / MONGO_DB_NAME, dj‑database‑url import fixed
│   urls.py
│   wsgi.py

volunteers/                # Core app for NGO logic
│   __init__.py
│   admin.py
│   apps.py
│   models.py           # Django ORM models (Volunteer, Campaign, Shift, …)
│   views.py            # Views for dashboards, campaign detail, etc.
│   forms.py            # ModelForm definitions
│   tests.py            # 4 unit tests covering models & helper functions
│   urls.py             # URL patterns for the app (already present)
│   context_processors.py  # now injects `mongo_online` & `mongo_status_msg`
│   mongo.py            # **Full PyMongo integration** – client singleton, fallback, validation, CRUD helpers
│   migrations/         # initial migration
│   management/commands/seed_data.py  # optional seed script

static/ & staticfiles/    # CSS/JS – includes `gov-theme.css` for Indian‑government‑style UI
templates/                # HTML templates (base.html, volunteer_dashboard.html, …)
    volunteers/ …        # app‑specific templates
    registration/ …      # login template

media/                    # uploaded avatars & campaign banners (empty placeholders)

build.sh, render.yaml      # deployment helpers for Render (already configured)
```
All directories are present and referenced correctly by `settings.py` (STATIC_ROOT, MEDIA_ROOT, TEMPLATE_DIRS).

---

## 🗄️ MongoDB Integration (`volunteers/mongo.py`)
| Feature | Implementation Details |
|---------|------------------------|
| **Client singleton** | `get_client()` creates a `MongoClient` with a 1.5 s server‑selection timeout. Returns a cached client or `None` if connection fails.
| **Online flag** | `is_mongo_online()` – used by the context processor to expose `mongo_online` (bool) and a friendly `mongo_status_msg`.
| **Fallback storage** | In‑memory Python lists (`_fallback_ops`, `_fallback_feedback`, `_fallback_dispatch`). Used when MongoDB is unreachable; IDs are generated with `uuid4()` to mimic ObjectId.
| **Validation helpers** | Functions `validate_operation_log(data)`, `validate_feedback(data)`, `validate_dispatch(data)` – return a list of error strings; CRUD wrappers raise `ValueError` on validation failure.
| **Generic CRUD helpers** | Private functions `_insert_one`, `_find_one`, `_find_many`, `_update_one`, `_delete_one` handle both real collection and fallback list.
| **Specific CRUD APIs** | `insert_operation_log`, `list_operation_logs`, `get_operation_log`, `update_operation_log`, `delete_operation_log` (similarly for feedback & dispatch). All return plain Python dicts, making them easy to render in templates or API responses.
| **Error handling** | All public helpers catch `pymongo.errors.PyMongoError` and fall back to in‑memory storage, ensuring the app never crashes because of DB outage.

**Usage example (in a view):**
```python
from volunteers.mongo import insert_operation_log, list_operation_logs

if request.method == "POST":
    try:
        new_log = insert_operation_log(request.POST)
    except ValueError as exc:
        return render(request, "error.html", {"msg": str(exc)})
    return redirect("operations_dashboard")

logs = list_operation_logs()
return render(request, "volunteers/operations_dashboard.html", {"logs": logs})
```
The view can check `request.context["mongo_online"]` (provided by the context processor) to display a status badge.

---

## 🚀 Running the Project Locally
1. **Clone / open the repository** (already done).
2. **Create a virtual environment & install deps** (already executed):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Configure environment variables** (add to a `.env` file or export):
   ```bash
   export DJANGO_SECRET_KEY='your-secret-key'
   export DJANGO_DEBUG=True
   export DATABASE_URL='sqlite:///db.sqlite3'   # or any Postgres URL
   export MONGO_URI='mongodb://localhost:27017'   # point to a running MongoDB instance
   export MONGO_DB_NAME='ngo_portal'
   ```
   The `settings.py` reads `MONGO_URI` and `MONGO_DB_NAME` via `os.getenv`.
4. **Start MongoDB (optional)** – if you want real persistence:
   ```bash
   brew install mongodb-community@7   # macOS Homebrew
   mongod --config /opt/homebrew/etc/mongod.conf &
   ```
   If MongoDB is not running, the app will automatically use the in‑memory fallback.
5. **Apply migrations & start the dev server**:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
6. **Visit the site** – open `http://127.0.0.1:8000/` in a browser. The navigation bar will show a MongoDB status indicator (green = online, orange = fallback).
7. **Run the test suite** (optional sanity check):
   ```bash
   python manage.py test volunteers
   ```
   All 4 tests should pass.

---

## 📦 Deployment on Render
The repository already contains `render.yaml` and `build.sh`. After pushing commits to the linked Git repo, Render will:
1. Install the Python runtime.
2. Run `pip install -r requirements.txt`.
3. Execute `build.sh` (collect static files, apply migrations).
4. Start the web service with `gunicorn ngo_portal.wsgi`.

**Important:** Ensure the Render environment has the same environment variables as in step 3 (especially `MONGO_URI`). Render provides a managed MongoDB add‑on; use its connection string.

---

## 📌 What’s Still Missing / Next Steps (if you want more)
- **URL & view wiring for CRUD pages** – currently the Mongo helpers exist but no dedicated UI pages expose them. Add routes in `volunteers/urls.py` and corresponding templates (`operations_list.html`, `operations_form.html`, etc.).
- **Unit tests for the Mongo helpers** – only Django model tests exist. Consider adding tests that simulate both online and fallback modes.
- **Authentication / permissions** – protect CRUD endpoints with `@login_required` or Django’s permission system.
- **Static assets polish** – you mentioned a “government website” look; replace placeholder images in `static/images/` with your NGO branding and adjust `gov-theme.css` as needed.

---

### TL;DR
- All Python files compile, Django checks clean, and the test suite passes.
- `volunteers/mongo.py` now provides a complete, validated PyMongo layer with graceful fallback.
- You can run the app locally with the steps above; it will work even without a Mongo instance.
- Deployment to Render is already set up – just push and set the required environment variables.

Feel free to ask for any of the missing UI pages, additional tests, or deployment tweaks!

