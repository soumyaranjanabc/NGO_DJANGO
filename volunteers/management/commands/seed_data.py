import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from volunteers.models import (
    VolunteerProfile, Campaign, Activity, VolunteerAvailability,
    Role, Shift, ShiftAssignment, ParticipationRecord, Announcement
)


class Command(BaseCommand):
    help = "Populate realistic sample data for the NGO Volunteer Operations Platform"

    def add_arguments(self, parser):
        parser.add_argument(
            '--if-empty',
            action='store_true',
            help='Only seed if no campaigns currently exist in the database',
        )

    def handle(self, *args, **options):
        if options.get('if_empty') and Campaign.objects.exists():
            self.stdout.write(self.style.SUCCESS("Database already contains data; skipping seed."))
            return

        self.stdout.write("Initializing Seva Platform seed data...")

        # 1. Superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@ngo-portal.gov.in',
                password='adminpassword123',
                first_name='Director',
                last_name='General'
            )
            VolunteerProfile.objects.create(
                user=admin,
                phone='9811002026',
                state='New Delhi',
                district='Central Delhi',
                occupation='Chief Operations Officer',
                skills='National Coordination, Disaster Operations, Strategic Relief',
                is_coordinator=True,
                verification_status='VERIFIED'
            )
            self.stdout.write("Created Superuser: admin / adminpassword123")

        # 2. Operations Coordinator
        coord_user, created = User.objects.get_or_create(
            username='coordinator',
            defaults={
                'email': 'coordinator@ngo-portal.gov.in',
                'first_name': 'Virender',
                'last_name': 'Nath'
            }
        )
        if created:
            coord_user.set_password('seva@2026')
            coord_user.save()
            VolunteerProfile.objects.create(
                user=coord_user,
                phone='9876500001',
                emergency_contact_name='Suman Nath',
                emergency_contact_phone='9876500002',
                blood_group='O+',
                state='New Delhi',
                district='Central Delhi',
                occupation='Disaster Response Officer',
                skills='Field Leadership, Incident Command, Logistics, Triage',
                is_coordinator=True,
                verification_status='VERIFIED'
            )
            self.stdout.write("Created Coordinator: coordinator / seva@2026")

        # 3. Volunteers
        volunteers_data = [
            {
                'username': 'volunteer1',
                'first_name': 'Rajesh',
                'last_name': 'Kumar',
                'email': 'rajesh.kumar@email.in',
                'phone': '9876123451',
                'state': 'New Delhi',
                'district': 'South Delhi',
                'blood_group': 'B+',
                'occupation': 'IT Consultant',
                'skills': 'First Aid, Tech Support, Supply Chain, Driving',
                'sector': 'Disaster & Community Relief',
                'bio': 'Passionate about humanitarian logistics and rapid response volunteerism.'
            },
            {
                'username': 'volunteer2',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'email': 'priya.sharma@email.in',
                'phone': '9876123452',
                'state': 'Maharashtra',
                'district': 'Mumbai Suburban',
                'blood_group': 'A+',
                'occupation': 'Registered Nurse',
                'skills': 'Medical Nursing, Health Screening, Vitals Check, Counseling',
                'sector': 'Healthcare & Medical Relief',
                'bio': 'Medical professional dedicating weekends to rural health camps.'
            },
            {
                'username': 'volunteer3',
                'first_name': 'Amit',
                'last_name': 'Verma',
                'email': 'amit.verma@email.in',
                'phone': '9876123453',
                'state': 'Odisha',
                'district': 'Cuttack',
                'blood_group': 'O+',
                'occupation': 'College Lecturer',
                'skills': 'Teaching, Community Mobilization, Translation, Crowd Control',
                'sector': 'Pratham Shiksha & Rural Literacy',
                'bio': 'Committed to empowering underprivileged children through weekend literacy drives.'
            },
            {
                'username': 'volunteer4',
                'first_name': 'Sunita',
                'last_name': 'Patel',
                'email': 'sunita.patel@email.in',
                'phone': '9876123454',
                'state': 'Gujarat',
                'district': 'Ahmedabad',
                'blood_group': 'AB+',
                'occupation': 'Social Worker',
                'skills': 'Dry Ration Packing, Inventory Desk, Women Empowerment, Counseling',
                'sector': 'Annapurna Food Security & Ration',
                'bio': 'Working on zero-hunger community kitchens and relief nutrition.'
            },
        ]

        vol_objs = []
        for v in volunteers_data:
            user, u_created = User.objects.get_or_create(
                username=v['username'],
                defaults={
                    'first_name': v['first_name'],
                    'last_name': v['last_name'],
                    'email': v['email']
                }
            )
            if u_created:
                user.set_password('seva@2026')
                user.save()
                profile = VolunteerProfile.objects.create(
                    user=user,
                    phone=v['phone'],
                    state=v['state'],
                    district=v['district'],
                    blood_group=v['blood_group'],
                    occupation=v['occupation'],
                    skills=v['skills'],
                    preferred_sector=v['sector'],
                    bio=v['bio'],
                    verification_status='VERIFIED',
                    availability_status='AVAILABLE'
                )
                vol_objs.append(profile)

                # Add weekly availability
                VolunteerAvailability.objects.create(
                    volunteer=profile,
                    day_of_week='SATURDAY',
                    time_slot='MORNING',
                    notes='Ready for field duty'
                )
                VolunteerAvailability.objects.create(
                    volunteer=profile,
                    day_of_week='SUNDAY',
                    time_slot='FULL_DAY',
                    notes='Can travel within district'
                )
            else:
                vol_objs.append(user.volunteer_profile)

        # 4. Standard Operational Roles
        roles_data = [
            {
                'name': 'Field Marshall & Squad Lead',
                'code': 'MARSHALL',
                'description': 'Directs ground squads, verifies volunteer check-ins, enforces safety protocol.',
                'key_responsibilities': 'Supervise 10-15 volunteers, liaison with local administration, coordinate relief dispatch.',
                'required_skills': 'Leadership, Disaster Drill, Crowd Marshalling',
                'is_field_role': True
            },
            {
                'name': 'First Aid & Emergency Triage Medic',
                'code': 'FIRST_AID',
                'description': 'Administers on-site basic first aid, triage, and vitals assessment.',
                'key_responsibilities': 'Maintain medical kit, attend heat exhaustion / minor injuries, escalate to ambulance.',
                'required_skills': 'First Aid Certified, Nursing, Medical Triage',
                'is_field_role': True
            },
            {
                'name': 'Relief Supply & Logistics Officer',
                'code': 'SUPPLY_LOGISTICS',
                'description': 'Oversees packing, inventory tracking, and warehouse dispatch of relief kits.',
                'key_responsibilities': 'Track ration bags, unload vehicles, manage distribution point counters.',
                'required_skills': 'Inventory Management, Heavy Lifting, Team Coordination',
                'is_field_role': True
            },
            {
                'name': 'Citizen Registration Desk In-Charge',
                'code': 'REG_DESK',
                'description': 'Registers beneficiaries, validates tokens, and verifies identity documents.',
                'key_responsibilities': 'Token verification, queue management, helpdesk assistance.',
                'required_skills': 'Communication, Local Language, Data Entry',
                'is_field_role': True
            },
            {
                'name': 'Community Literacy Guide',
                'code': 'LITERACY_GUIDE',
                'description': 'Conducts activity-based learning sessions and distributes study materials to children.',
                'key_responsibilities': 'Teach basic numeracy and reading, organize games, supervise study halls.',
                'required_skills': 'Teaching, Patience, Child Psychology',
                'is_field_role': True
            },
        ]

        role_objs = {}
        for r in roles_data:
            role_obj, _ = Role.objects.get_or_create(code=r['code'], defaults=r)
            role_objs[r['code']] = role_obj

        # 5. Realistic Indian NGO Campaigns
        today = timezone.localdate()

        campaigns_data = [
            {
                'title': 'Aapda Seva: Coastal Cyclone & Flood Relief Mobilization',
                'slug': 'aapda-seva-coastal-relief-2026',
                'sector': 'DISASTER',
                'short_description': 'Emergency ground relief distributing dry rations, drinking water, and first aid kits to coastal flood-affected families.',
                'detailed_description': (
                    "In response to recent severe weather and coastal inundation, the National Volunteer Directorate has activated "
                    "emergency field relief base camps across affected blocks. Volunteer teams will assist in assembling dry ration kits, "
                    "managing water purification packet distribution, and operating citizen helpdesks. All volunteers will report in official "
                    "safety vests and carry personal identification."
                ),
                'target_beneficiaries': 5000,
                'target_volunteers': 60,
                'state': 'Odisha',
                'district': 'Cuttack',
                'venue_address': 'Central Relief Transit Camp, Near Barabati Stadium Complex, Cuttack',
                'start_date': today - datetime.timedelta(days=2),
                'end_date': today + datetime.timedelta(days=12),
                'status': 'ACTIVE',
                'emergency_helpline': '1800-11-2026 / 0671-2300456'
            },
            {
                'title': 'Pratham Shiksha: Urban Slum Evening Learning Centers',
                'slug': 'pratham-shiksha-evening-centers-2026',
                'sector': 'EDUCATION',
                'short_description': 'Dedicated youth volunteer teachers providing foundational literacy, STEM kits, and nutrition snacks to out-of-school children.',
                'detailed_description': (
                    "Pratham Shiksha aims to bridge educational disparities among underprivileged children in urban clusters. "
                    "Volunteers conduct engaging 2-hour daily learning circles focusing on Hindi, English phonics, and basic mathematics, "
                    "followed by distribution of fortified nutrition snacks and hygiene kits."
                ),
                'target_beneficiaries': 1500,
                'target_volunteers': 40,
                'state': 'Delhi',
                'district': 'Central Delhi',
                'venue_address': 'Community Centre & Open Learning Hall, Daryaganj, New Delhi',
                'start_date': today - datetime.timedelta(days=10),
                'end_date': today + datetime.timedelta(days=45),
                'status': 'ACTIVE',
                'emergency_helpline': '1800-11-2026'
            },
            {
                'title': 'Annapurna Seva: Daily Hot Meal & Community Ration Drive',
                'slug': 'annapurna-daily-food-bank-2026',
                'sector': 'FOOD',
                'short_description': 'Preparation and distribution of 2,500 daily wholesome meals to daily-wage workers, hospital attendants, and homeless families.',
                'detailed_description': (
                    "Annapurna Seva operates a centralized zero-waste community kitchen. Volunteers assist in raw vegetable preparation, "
                    "hygienic packaging of food trays, and scheduled dispatch to major public hospitals and transit shelters."
                ),
                'target_beneficiaries': 10000,
                'target_volunteers': 75,
                'state': 'Maharashtra',
                'district': 'Mumbai Suburban',
                'venue_address': 'Sewa Bhavan Community Kitchen, Andheri East, Mumbai',
                'start_date': today - datetime.timedelta(days=5),
                'end_date': today + datetime.timedelta(days=25),
                'status': 'ACTIVE',
                'emergency_helpline': '1800-11-2026 / 022-26830000'
            },
            {
                'title': 'Swachh Nadi: Yamuna Riverfront Restoration & Cleanliness Drive',
                'slug': 'swachh-nadi-yamuna-restoration-2026',
                'sector': 'ENVIRONMENT',
                'short_description': 'Civic volunteer task force organizing riverbank plastic collection, eco-awareness drives, and planting native soil-binding reeds.',
                'detailed_description': (
                    "A massive weekend mobilization under the Swachh Bharat mission to remove non-biodegradable plastics from river ghats, "
                    "segregate recyclable waste, and install community trash collection bins along the embankment."
                ),
                'target_beneficiaries': 25000,
                'target_volunteers': 120,
                'state': 'Delhi',
                'district': 'East Delhi',
                'venue_address': 'Kudsia Ghat & Wazirabad Embankment Entry Point, Delhi',
                'start_date': today + datetime.timedelta(days=2),
                'end_date': today + datetime.timedelta(days=20),
                'status': 'UPCOMING',
                'emergency_helpline': '1800-11-2026'
            },
        ]

        created_campaigns = []
        for cd in campaigns_data:
            c_obj, _ = Campaign.objects.get_or_create(
                slug=cd['slug'],
                defaults={
                    'title': cd['title'],
                    'sector': cd['sector'],
                    'short_description': cd['short_description'],
                    'detailed_description': cd['detailed_description'],
                    'target_beneficiaries': cd['target_beneficiaries'],
                    'target_volunteers': cd['target_volunteers'],
                    'state': cd['state'],
                    'district': cd['district'],
                    'venue_address': cd['venue_address'],
                    'start_date': cd['start_date'],
                    'end_date': cd['end_date'],
                    'status': cd['status'],
                    'lead_coordinator': coord_user,
                    'emergency_helpline': cd['emergency_helpline'],
                }
            )
            created_campaigns.append(c_obj)

        # 6. Activities for Campaign 1 & 2
        camp1 = created_campaigns[0]
        Activity.objects.get_or_create(
            campaign=camp1,
            title='Dry Ration Packing & Kit Assembly',
            defaults={
                'description': 'Packaging rice, pulses, oil, salt, and water purification tablets.',
                'required_skill': 'Packaging, Logistics',
                'target_metric': '2,500 Emergency Kits'
            }
        )
        Activity.objects.get_or_create(
            campaign=camp1,
            title='Mobile Medical Triage & First Aid',
            defaults={
                'description': 'Checking vitals, dressing flood wounds, and dispensing ORS packets.',
                'required_skill': 'Nursing, First Aid',
                'target_metric': '1,000 Patient Screenings'
            }
        )

        camp2 = created_campaigns[1]
        Activity.objects.get_or_create(
            campaign=camp2,
            title='Foundational Numeracy & Reading Circles',
            defaults={
                'description': 'Teaching basic alphabets, words, and addition through pictorial flashcards.',
                'required_skill': 'Teaching, Patience',
                'target_metric': '400 Children Taught'
            }
        )

        # 7. Scheduled Shifts
        # Completed shift (to showcase past attendance and verified certificate)
        past_shift, _ = Shift.objects.get_or_create(
            campaign=camp1,
            title='Phase-1 Emergency Ration Assembly Duty',
            date=today - datetime.timedelta(days=1),
            defaults={
                'start_time': datetime.time(8, 0),
                'end_time': datetime.time(14, 0),
                'reporting_location': 'Warehouse Gate 3, Central Relief Transit Camp, Cuttack',
                'in_charge_name': 'Virender Nath (Nodal Officer)',
                'in_charge_contact': '+91 9876500001',
                'required_volunteers': 15,
                'status': 'COMPLETED',
                'special_instructions': 'Wear safety gloves and NGO badge. Heavy lifting involved.'
            }
        )

        # Assign volunteers to past shift and finalize participation records
        v1 = vol_objs[0]  # Rajesh Kumar
        v2 = vol_objs[1]  # Priya Sharma

        assign1, _ = ShiftAssignment.objects.get_or_create(
            shift=past_shift,
            volunteer=v1,
            defaults={
                'role': role_objs['SUPPLY_LOGISTICS'],
                'status': 'COMPLETED',
                'assigned_by': coord_user,
                'admin_notes': 'Appointed as warehouse logistics assistant.'
            }
        )
        assign2, _ = ShiftAssignment.objects.get_or_create(
            shift=past_shift,
            volunteer=v2,
            defaults={
                'role': role_objs['FIRST_AID'],
                'status': 'COMPLETED',
                'assigned_by': coord_user,
                'admin_notes': 'Appointed as duty triage medic.'
            }
        )

        # Create verified participation records with certificates!
        ParticipationRecord.objects.get_or_create(
            assignment=assign1,
            defaults={
                'attendance_status': 'PRESENT',
                'hours_logged': Decimal('6.00'),
                'performance_rating': 5,
                'coordinator_remarks': 'Exemplary dedication. Organized 400 ration boxes swiftly.',
                'certificate_code': 'NGO-SEVA-2026-RAJESH01'
            }
        )
        ParticipationRecord.objects.get_or_create(
            assignment=assign2,
            defaults={
                'attendance_status': 'PRESENT',
                'hours_logged': Decimal('6.00'),
                'performance_rating': 5,
                'coordinator_remarks': 'Handled first-aid for 45 flood relief workers.',
                'certificate_code': 'NGO-SEVA-2026-PRIYA002'
            }
        )

        # Upcoming active shifts
        upcoming_shift_1, _ = Shift.objects.get_or_create(
            campaign=camp1,
            title='Morning Flood Relief Dispatch & Camp Triage',
            date=today + datetime.timedelta(days=1),
            defaults={
                'start_time': datetime.time(9, 0),
                'end_time': datetime.time(13, 0),
                'reporting_location': 'Shelter Pavilion, Near Barabati Stadium, Cuttack',
                'in_charge_name': 'Virender Nath',
                'in_charge_contact': '+91 9876500001',
                'required_volunteers': 12,
                'status': 'SCHEDULED',
                'special_instructions': 'Bring Aadhaar/Govt ID card. Report 15 minutes prior to commencement.'
            }
        )

        upcoming_shift_2, _ = Shift.objects.get_or_create(
            campaign=camp2,
            title='Weekend Learning Circle & Activity Hour',
            date=today + datetime.timedelta(days=2),
            defaults={
                'start_time': datetime.time(15, 0),
                'end_time': datetime.time(18, 0),
                'reporting_location': 'Room 102, Daryaganj Community Centre, New Delhi',
                'in_charge_name': 'Meera Sen',
                'in_charge_contact': '+91 9811223344',
                'required_volunteers': 10,
                'status': 'SCHEDULED',
                'special_instructions': 'Carry notebook, pens, and flashcards provided by NGO office.'
            }
        )

        upcoming_shift_3, _ = Shift.objects.get_or_create(
            campaign=created_campaigns[2],
            title='Annapurna Morning Meal Packaging Shift',
            date=today + datetime.timedelta(days=3),
            defaults={
                'start_time': datetime.time(6, 30),
                'end_time': datetime.time(10, 30),
                'reporting_location': 'Central Dispatch Bay, Sewa Bhavan, Andheri East, Mumbai',
                'in_charge_name': 'Kailash Joshi',
                'in_charge_contact': '+91 9820011223',
                'required_volunteers': 20,
                'status': 'SCHEDULED',
                'special_instructions': 'Aprons and hair nets provided at entrance. Adhere to kitchen hygiene norms.'
            }
        )

        # Enroll volunteer1 in upcoming shift 1
        ShiftAssignment.objects.get_or_create(
            shift=upcoming_shift_1,
            volunteer=v1,
            defaults={
                'role': role_objs['MARSHALL'],
                'status': 'APPROVED',
                'assigned_by': coord_user,
                'admin_notes': 'Lead Marshall for South Pavilion squad.'
            }
        )

        # 8. Notice Ticker Announcements
        announcements_data = [
            {
                'title': 'Aapda Seva: Coastal Cyclone Base Camp Activated in Cuttack',
                'campaign': camp1,
                'message': '50 emergency volunteers dispatched. Relief supply dispatch scheduled daily from 08:00 AM.',
                'priority': 'EMERGENCY',
                'is_published': True
            },
            {
                'title': 'Verified Digital Certificates for Q1 2026 Available for Download',
                'campaign': None,
                'message': 'Volunteers who completed their shifts can view and print verifiable certificates with QR codes.',
                'priority': 'IMPORTANT',
                'is_published': True
            },
            {
                'title': 'Weekend Yamuna Riverfront Afforestation & Cleanup Drive Enrollment Open',
                'campaign': created_campaigns[3],
                'message': 'Citizen volunteers invited for tree plantation and waste segregation at Kudsia Ghat this Saturday.',
                'priority': 'NORMAL',
                'is_published': True
            },
        ]

        for a in announcements_data:
            Announcement.objects.get_or_create(
                title=a['title'],
                defaults=a
            )

        self.stdout.write(self.style.SUCCESS("✓ Seed data initialized successfully!"))
        self.stdout.write(self.style.SUCCESS("Review accounts:"))
        self.stdout.write("  - Admin / Coordinator: coordinator / seva@2026")
        self.stdout.write("  - Volunteer User:      volunteer1 / seva@2026")
        self.stdout.write("  - Verified Cert Code:  NGO-SEVA-2026-RAJESH01")
