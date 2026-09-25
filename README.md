# राष्ट्रीय सेवा सेतु (Rashtriya Seva Setu)
## National NGO Volunteer Operations & Mobilization Platform

An enterprise-grade, comprehensive Django web platform designed to eliminate manual coordination of volunteers, campaigns, activities, availability, role assignments, shift scheduling, ground participation, and digital certification.

Built with an **authentic Government of India Portal aesthetic** (inspired by *MyGov*, *National Portal of India (india.gov.in)*, *Digital India*, and the *National Service Scheme (NSS)*) with deep accessibility features, Tiranga tricolor styling, and full readiness for **Render** cloud deployment.

---

## 🌟 Key Platform Modules & Functionalities

### 1. 🪪 Volunteer Profiles & Identity Verification
- Official **Seva ID Card** generation (`SEVA-YYYY-XXXX`).
- Multi-field volunteer profile: Phone, Alternate Phone, Emergency Contacts, Blood Group, Gender, State, District, PIN code, and Permanent Address.
- Official ID Proof Support: Aadhaar, Voter ID, PAN, Driving License, Student/College ID.
- Skill directory (Medical/First Aid, Teaching, Logistics, Crowd Control, Driving, Tech Support).
- Availability Status Switcher (Available, On Duty, On Leave, Inactive).
- Service Recognition Tiers (Bronze, Silver, Gold, National Seva Ratna).
- Profile photo upload with Gov Seva Avatar fallback.

### 2. 📢 Campaign & Humanitarian Relief Management
- Campaign Directory with sector tags:
  - *Healthcare & Medical Relief*
  - *Pratham Shiksha & Rural Literacy*
  - *Swachh Bharat & Urban Afforestation*
  - *Aapda Seva (Disaster Response)*
  - *Annapurna Food Security & Ration*
- Target Beneficiaries vs. Volunteers Mobilized live calculation.
- Granular sub-activities under campaigns (e.g., *Ration Kit Packing*, *Vitals Check*, *Numeracy Circles*).
- Field venue reporting details, base camp locations, and emergency helpline desk numbers.

### 3. 📅 Volunteer Availability & Shift Scheduling
- Recurring weekly availability scheduler (Mornings, Afternoons, Evenings, Weekends, 24x7 Emergency On-Call).
- Operational Shifts linked to Campaigns and Activities with specific reporting venues and ground in-charge contacts.
- Volunteer capacity quotas and real-time slot tracking (`X / Y filled`, automatic waitlisting when full).
- Self-enrollment for volunteers with preferred role selection.

### 4. 👥 Role Assignment & Shift Roster Controller
- Specialized roles: *Field Marshall & Squad Lead*, *First Aid & Triage Medic*, *Relief Logistics Officer*, *Registration Desk In-Charge*, *Community Literacy Guide*.
- Coordinator Roster Management dashboard to approve applicants, assign specialized roles, or move volunteers to waitlists.

### 5. ✍️ Ground Attendance & Participation Tracking
- **One-Click Batch Attendance Sheet** for Shift Coordinators:
  - Mark volunteers as *Present*, *Absent*, *Late*, or *Excused*.
  - Automatically calculates and logs service hours.
  - 1-to-5 star performance rating and coordinator merit notes.
  - Automatically generates unique verifiable digital certificate codes (`NGO-SEVA-YYYY-XXXXXXXX`).

### 6. 📜 Digital Certificate of Appreciation & Public Verification
- Printable official **Certificate of Appreciation**:
  - Double navy & gold border frame with corner motifs.
  - Ashoka Chakra / NGO seal watermark.
  - Conferred volunteer name, Seva ID, campaign, shift title, role, and verified hours logged.
  - Dual official signatures: *Director of Field Operations* and *National Secretary*.
  - Hidden controls on print (`window.print()` prints clean certificate).
- **Public Certificate Verification Portal** (`/verify-certificate/`):
  - Allows employers, colleges, and authorities to verify certificate authenticity via security code.

### 7. 🎛️ Operations Command Center & Data Export
- Coordinator / Officer Command Dashboard:
  - Live KPIs: Total registered volunteers, Active campaigns, Pending shift sign-offs, Total hours served.
  - One-click CSV export:
    - **Volunteer Directory CSV**: Full list with contact info, skills, and hours.
    - **Attendance & Participation Audit Log CSV**: Complete verification logs.
- Urgent circulars and notice broadcasting with portal top ticker.

---

## 🎨 Indian Government Portal Aesthetic & Accessibility

The portal incorporates standard features prescribed under the **Guidelines for Indian Government Websites (GIGW)**:
- **Top Utility & Accessibility Bar**:
  - `A-`, `A`, `A+` live font-size resizer (persisted in `localStorage`).
  - **High-Contrast Dark Mode Toggle** (Gov.in standard high-contrast palette).
  - Live **Indian Standard Time (IST)** clock.
  - Language indicator (English / हिन्दी).
  - Skip to main content link for screen-readers.
- **Tiranga National Accent Ribbon**:
  - 3-color Saffron (`#FF9933`), White (`#FFFFFF`), and Green (`#138808`) linear gradient strips.
- **Official Seals & Typography**:
  - Clean typography (`Inter`, `Noto Sans Devanagari`).
  - Formal Government table layouts, badges, and embossed card designs.

---

## 📸 How to Add Your Own NGO Images (Template Comments)

Clear HTML and Django comments have been left in all relevant templates so you can replace the placeholder designs with your own NGO assets:

| Image Asset | Location in Code | Where to Place Your File |
| :--- | :--- | :--- |
| **Official NGO Logo** | [`templates/base.html`](file:///Users/soumyaranjanmohanty/Documents/NGO_DJANGO/templates/base.html#L70-L115) | Save image at `static/images/ngo-logo.png` and uncomment `<img>` tag |
| **Hero Field Banner** | [`templates/volunteers/home.html`](file:///Users/soumyaranjanmohanty/Documents/NGO_DJANGO/templates/volunteers/home.html#L55-L85) | Save image at `static/images/hero-ngo-banner.jpg` and uncomment `<img>` |
| **Gallery Field Photos** | [`templates/volunteers/home.html`](file:///Users/soumyaranjanmohanty/Documents/NGO_DJANGO/templates/volunteers/home.html#L240-L315) | Save photos in `static/images/gallery/` (`photo1.jpg`, `photo2.jpg`, etc.) |
| **Campaign Banners** | Uploaded via Campaign Form or Admin | Automatically uploaded to `media/campaigns/banners/` |
| **Volunteer Avatars** | Uploaded during registration or profile edit | Automatically uploaded to `media/volunteers/avatars/` |
| **Certificate Stamp/Seal** | [`templates/volunteers/certificate.html`](file:///Users/soumyaranjanmohanty/Documents/NGO_DJANGO/templates/volunteers/certificate.html#L80-L105) | Save stamp at `static/images/ngo-stamp.png` |

---

## 🚀 Running Locally

### 1. Activate Virtual Environment
```bash
cd /Users/soumyaranjanmohanty/Documents/NGO_DJANGO
source .venv/bin/activate
```

### 2. Apply Migrations & Seed Sample Data
```bash
python manage.py migrate
python manage.py seed_data
```

### 3. Run Development Server
```bash
python manage.py runserver 8000
```
Open your browser at `http://127.0.0.1:8000/`.

---

## 🔑 Demo Login Accounts

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Operations Coordinator** | `coordinator` | `seva@2026` | Full Operations Command, Rosters, Attendance, Shifts |
| **Citizen Volunteer** | `volunteer1` | `seva@2026` | Volunteer Self-Service Portal, Seva ID, Certificates |
| **Superuser / Admin** | `admin` | `adminpassword123` | Django Admin (`/admin/`) and all privileges |

*Test Certificate Verification Code:* `NGO-SEVA-2026-RAJESH01` on `/verify-certificate/`.

---

## ☁️ Deploying to Render

Full deployment instructions are available in [`RENDER_DEPLOYMENT.md`](file:///Users/soumyaranjanmohanty/Documents/NGO_DJANGO/RENDER_DEPLOYMENT.md).

Quick summary:
1. Push this repository to GitHub.
2. In Render, select **New +** -> **Web Service**.
3. Set **Build Command** to `./build.sh` and **Start Command** to `gunicorn ngo_portal.wsgi:application`.
4. Render will automatically build the environment, collect static assets, run database migrations, and launch the service with WhiteNoise and Gunicorn.
