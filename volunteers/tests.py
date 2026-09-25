from decimal import Decimal
from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from volunteers.models import (
    VolunteerProfile, Campaign, Shift, Role,
    ShiftAssignment, ParticipationRecord
)


class VolunteerPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create coordinator user
        self.coord_user = User.objects.create_user(
            username='coordinator_test',
            password='testpassword123',
            first_name='Coordinator',
            last_name='User'
        )
        self.coord_profile = VolunteerProfile.objects.create(
            user=self.coord_user,
            phone='9999999991',
            state='Delhi',
            district='Central',
            is_coordinator=True,
            verification_status='VERIFIED'
        )

        # Create volunteer user
        self.vol_user = User.objects.create_user(
            username='volunteer_test',
            password='testpassword123',
            first_name='Aarav',
            last_name='Sharma'
        )
        self.vol_profile = VolunteerProfile.objects.create(
            user=self.vol_user,
            phone='9999999992',
            state='Delhi',
            district='Central',
            skills='First Aid, Logistics',
            is_coordinator=False,
            verification_status='VERIFIED'
        )

        # Create test campaign
        self.campaign = Campaign.objects.create(
            title='Delhi Relief Mission',
            slug='delhi-relief-mission',
            sector='DISASTER',
            short_description='Emergency test drive',
            detailed_description='Full test scope',
            target_beneficiaries=500,
            target_volunteers=20,
            state='Delhi',
            district='Central',
            venue_address='Red Cross Bhavan, New Delhi',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            status='ACTIVE'
        )

        # Create test role
        self.role = Role.objects.create(
            name='First Aid Specialist',
            code='FIRST_AID_TEST',
            description='Medical triage and dressing'
        )

        # Create test shift
        self.shift = Shift.objects.create(
            campaign=self.campaign,
            title='Morning First Aid Shift',
            date=date.today() + timedelta(days=1),
            start_time=time(9, 0),
            end_time=time(13, 0),
            reporting_location='Camp Tent A, Red Cross Bhavan',
            in_charge_name='Dr. Coordinator',
            in_charge_contact='+91 9999999991',
            required_volunteers=5,
            status='SCHEDULED'
        )

    def test_home_page_renders_successfully(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "राष्ट्रीय सेवा सेतु")
        self.assertContains(response, "Delhi Relief Mission")

    def test_campaign_list_and_detail(self):
        response = self.client.get(reverse('campaign_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delhi Relief Mission")

        detail_resp = self.client.get(reverse('campaign_detail', kwargs={'slug': self.campaign.slug}))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, "Morning First Aid Shift")

    def test_volunteer_shift_application(self):
        self.client.login(username='volunteer_test', password='testpassword123')
        apply_url = reverse('apply_for_shift', kwargs={'shift_id': self.shift.id})
        
        response = self.client.post(apply_url, {'role_id': self.role.id}, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify assignment was recorded in DB
        assignment = ShiftAssignment.objects.filter(shift=self.shift, volunteer=self.vol_profile).first()
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment.status, 'APPROVED')
        self.assertEqual(assignment.role, self.role)

    def test_batch_attendance_and_certificate_issuance(self):
        # First assign volunteer
        assignment = ShiftAssignment.objects.create(
            shift=self.shift,
            volunteer=self.vol_profile,
            role=self.role,
            status='APPROVED'
        )

        # Coordinator logs in and marks attendance
        self.client.login(username='coordinator_test', password='testpassword123')
        attendance_url = reverse('mark_shift_attendance', kwargs={'shift_id': self.shift.id})

        post_data = {
            f'status_{assignment.id}': 'PRESENT',
            f'hours_{assignment.id}': '4.0',
            f'rating_{assignment.id}': '5',
            f'remarks_{assignment.id}': 'Excellent duty performance',
        }
        resp = self.client.post(attendance_url, post_data, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Verify participation record created and certificate code generated
        record = ParticipationRecord.objects.filter(assignment=assignment).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.attendance_status, 'PRESENT')
        self.assertEqual(record.hours_logged, Decimal('4.00'))
        self.assertTrue(record.certificate_code.startswith('NGO-SEVA-'))

        # Verify volunteer total hours updated
        self.assertEqual(self.vol_profile.total_hours_served, 4.0)

        # Verify public certificate verification endpoint
        verify_url = f"{reverse('verify_certificate')}?code={record.certificate_code}"
        verify_resp = self.client.get(verify_url)
        self.assertEqual(verify_resp.status_code, 200)
        self.assertContains(verify_resp, "VERIFIED GENUINE SERVICE RECORD")
        self.assertContains(verify_resp, self.vol_user.get_full_name())
