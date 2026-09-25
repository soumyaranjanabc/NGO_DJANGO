# 🚀 Step-by-Step Guide: Deploying to Render

This Django NGO Volunteer Operations Platform is pre-configured for **1-click / automated deployment on [Render](https://render.com)**.

---

## 🛠 Included Deployment Configuration

The repository contains all required production files:
1. [`build.sh`](file:///Users/soumyaranjanmohanty/Documents/NGO_DJANGO/build.sh): Automatically runs `pip install`, `collectstatic`, `migrate`, and `seed_data --if-empty`.
2. [`render.yaml`](file:///Users/soumyaranjanmohanty/Documents/NGO_DJANGO/render.yaml): Blueprint defining service configuration, python version, and environment variables.
3. [`Procfile`](file:///Users/soumyaranjanmohanty/Documents/NGO_DJANGO/Procfile): Instructs Render to launch `gunicorn ngo_portal.wsgi:application`.
4. [`requirements.txt`](file:///Users/soumyaranjanmohanty/Documents/NGO_DJANGO/requirements.txt): Includes `django`, `whitenoise`, `gunicorn`, `dj-database-url`, `psycopg2-binary`, and `pillow`.
5. [`ngo_portal/settings.py`](file:///Users/soumyaranjanmohanty/Documents/NGO_DJANGO/ngo_portal/settings.py): Auto-detects Render `DATABASE_URL` (PostgreSQL) and serves static files through WhiteNoise.

---

## 📋 Steps to Deploy on Render

### Step 1: Push Your Code to GitHub / GitLab
In your local terminal, stage and commit the project:
```bash
git add .
git commit -m "Complete Indian Government aesthetic NGO volunteer platform"
```

Then create a new repository on GitHub (e.g. `ngo-volunteer-platform`) and push your code:
```bash
git remote add origin https://github.com/<your-username>/ngo-volunteer-platform.git
git branch -M main
git push -u origin main
```

---

### Step 2: Create a Web Service on Render
1. Go to [dashboard.render.com](https://dashboard.render.com) and log in.
2. Click **New +** in the top navigation and select **Web Service**.
3. Choose **Build and deploy from a Git repository** and connect your GitHub repository.
4. Fill in the deployment details:
   - **Name**: `ngo-volunteer-platform` (or any custom name)
   - **Region**: Choose closest to India (e.g., `Singapore` or `Oregon`)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn ngo_portal.wsgi:application`
   - **Instance Type**: `Free`

---

### Step 3: Configure Environment Variables
Under the **Environment Variables** section on Render, add:

| Key | Recommended Value | Description |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.12.4` | Matches development Python version |
| `DEBUG` | `False` | Disables debug mode in production |
| `SECRET_KEY` | *(Click "Generate" or paste random 50+ chars)* | Django production secret key |
| `ALLOWED_HOSTS` | `.onrender.com,localhost,127.0.0.1` | Allows Render domain |

*(Optional)* If you wish to use a PostgreSQL database instead of the built-in SQLite:
1. Click **New +** -> **PostgreSQL** on Render.
2. Copy the **Internal Database URL**.
3. Add an environment variable `DATABASE_URL` with the copied URL in your Web Service settings.

---

### Step 4: Click "Deploy Web Service"
1. Render will run `./build.sh`:
   - Installs dependencies from `requirements.txt`
   - Collects and hashes static files with WhiteNoise
   - Applies database migrations
   - Seeds initial sample campaigns and coordinator accounts
2. Once the build finishes, Render will output your live URL:
   `https://ngo-volunteer-platform.onrender.com`

---

## 🔑 Default Production Logins (Created by `seed_data`)
Once deployed, log in to test both views:
- **Operations Coordinator**:
  - Username: `coordinator`
  - Password: `seva@2026`
- **Citizen Volunteer**:
  - Username: `volunteer1`
  - Password: `seva@2026`
- **Superuser / Django Admin** (`/admin/`):
  - Username: `admin`
  - Password: `adminpassword123`
