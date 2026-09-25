import uuid
from decimal import Decimal
from datetime import datetime, date
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class VolunteerProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    ID_TYPE_CHOICES = [
        ('AADHAAR', 'Aadhaar Card'),
        ('VOTER_ID', 'Voter Identity Card (EPIC)'),
        ('PAN', 'PAN Card'),
        ('DRIVING_LICENSE', 'Driving License'),
        ('COLLEGE_ID', 'Student / College ID'),
        ('OTHER', 'Other Official Govt Photo ID'),
    ]

    AVAILABILITY_CHOICES = [
        ('AVAILABLE', 'Available for Deployment'),
        ('IN_SHIFT', 'Currently on Active Shift'),
        ('ON_LEAVE', 'On Leave / Blackout Period'),
        ('INACTIVE', 'Inactive'),
    ]

    VERIFICATION_CHOICES = [
        ('PENDING', 'Verification Pending'),
        ('VERIFIED', 'Verified Sevak / Volunteer'),
        ('REJECTED', 'Application Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile')
    volunteer_id = models.CharField(max_length=30, unique=True, blank=True, help_text="Official NGO Volunteer Registration ID")
    phone = models.CharField(max_length=15, help_text="Primary 10-digit mobile number")
    alternate_phone = models.CharField(max_length=15, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default='N')
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    
    # Official Identification (Standard for Indian Volunteer Reg. portals like NSS/NYKS)
    id_proof_type = models.CharField(max_length=30, choices=ID_TYPE_CHOICES, default='AADHAAR')
    id_proof_number = models.CharField(max_length=50, blank=True, help_text="Masked or Full ID Number")
    
    # Geographic Details
    state = models.CharField(max_length=100, default='New Delhi')
    district = models.CharField(max_length=100, default='Central Delhi')
    pincode = models.CharField(max_length=10, blank=True)
    address = models.TextField(blank=True)
    
    # Skills and Background
    occupation = models.CharField(max_length=100, blank=True, help_text="e.g. Student, Software Engineer, Doctor, Teacher, Social Worker")
    skills = models.TextField(default="Logistics, First Aid, Community Outreach", help_text="Comma-separated volunteer skills")
    preferred_sector = models.CharField(max_length=50, default="Disaster & Community Relief")
    bio = models.TextField(blank=True, help_text="Short volunteer statement or motivation")
    
    # Media: Profile Photo (User can replace with their own image)
    profile_picture = models.ImageField(upload_to='volunteers/avatars/', null=True, blank=True)
    
    # Status & Roles
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='AVAILABLE')
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='VERIFIED')
    is_coordinator = models.BooleanField(default=False, help_text="Grant Campaign / Shift Coordination privileges")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.volunteer_id:
            # Generate official Gov-style ID: SEVA-YYYY-XXXX
            year = datetime.now().year
            short_uuid = uuid.uuid4().hex[:6].upper()
            self.volunteer_id = f"SEVA-{year}-{short_uuid}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.volunteer_id})"

    @property
    def skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    @property
    def total_hours_served(self):
        # Calculate sum of approved hours from participation records
        hours = ParticipationRecord.objects.filter(
            assignment__volunteer=self,
            attendance_status__in=['PRESENT', 'LATE']
        ).aggregate(total=models.Sum('hours_logged'))['total']
        return round(float(hours or 0.0), 1)

    @property
    def completed_shifts_count(self):
        return ParticipationRecord.objects.filter(
            assignment__volunteer=self,
            attendance_status__in=['PRESENT', 'LATE']
        ).count()

    @property
    def tier_badge(self):
        hours = self.total_hours_served
        if hours >= 100:
            return {'name': 'National Seva Ratna', 'color': 'bg-amber-600', 'text': 'text-amber-800', 'level': 'Platinum'}
        elif hours >= 50:
            return {'name': 'Gold Volunteer', 'color': 'bg-yellow-500', 'text': 'text-yellow-800', 'level': 'Gold'}
        elif hours >= 20:
            return {'name': 'Silver Volunteer', 'color': 'bg-slate-400', 'text': 'text-slate-800', 'level': 'Silver'}
        else:
            return {'name': 'Seva Sahayak', 'color': 'bg-emerald-600', 'text': 'text-emerald-800', 'level': 'Bronze'}


class Campaign(models.Model):
    SECTOR_CHOICES = [
        ('HEALTH', 'Healthcare & Medical Relief'),
        ('EDUCATION', 'Pratham Shiksha & Rural Literacy'),
        ('ENVIRONMENT', 'Swachh Bharat & Afforestation'),
        ('DISASTER', 'Aapda Seva (Disaster Response)'),
        ('FOOD', 'Annapurna Food Security & Ration'),
        ('WOMEN_CHILD', 'Women Empowerment & Child Welfare'),
        ('CIVIC', 'Civic Action, Traffic & Sanitation'),
        ('ELDERLY', 'Senior Citizen Care & Support'),
    ]

    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming / Mobilizing'),
        ('ACTIVE', 'Active / Operational'),
        ('COMPLETED', 'Mission Completed'),
        ('PAUSED', 'Temporarily Suspended'),
    ]

    title = models.CharField(max_length=200, help_text="Campaign / Initiative Title")
    slug = models.SlugField(max_length=220, unique=True)
    sector = models.CharField(max_length=30, choices=SECTOR_CHOICES, default='CIVIC')
    short_description = models.CharField(max_length=300, help_text="Brief summary for notice boards and lists")
    detailed_description = models.TextField(help_text="Detailed campaign brief, scope of work, protocol")
    
    # Image: Campaign Hero/Banner (Placeholders commented in templates for custom NGO photo upload)
    banner_image = models.ImageField(upload_to='campaigns/banners/', null=True, blank=True)
    
    # Target Metrics
    target_beneficiaries = models.PositiveIntegerField(default=1000, help_text="Estimated people / families impacted")
    target_volunteers = models.PositiveIntegerField(default=50, help_text="Volunteers needed for this campaign")
    
    # Location
    state = models.CharField(max_length=100, default="Delhi")
    district = models.CharField(max_length=100, default="Central")
    venue_address = models.TextField(help_text="Exact field site or central assembly point")
    
    # Timeline
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Leadership & Emergency
    lead_coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='coordinated_campaigns')
    emergency_helpline = models.CharField(max_length=50, default="1800-11-2026", help_text="Toll-free or control room contact")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"

    def get_absolute_url(self):
        return reverse('campaign_detail', kwargs={'slug': self.slug})

    @property
    def coordinator_name(self):
        if self.lead_coordinator:
            return self.lead_coordinator.get_full_name() or self.lead_coordinator.username
        return "District Nodal Officer"

    @property
    def total_shifts_count(self):
        return self.shifts.count()

    @property
    def enrolled_volunteers_count(self):
        # Distinct volunteers assigned to any shift in this campaign
        return ShiftAssignment.objects.filter(
            shift__campaign=self,
            status__in=['APPROVED', 'COMPLETED']
        ).values('volunteer').distinct().count()

    @property
    def mobilization_percentage(self):
        if self.target_volunteers <= 0:
            return 100
        pct = (self.enrolled_volunteers_count / self.target_volunteers) * 100
        return min(round(pct, 1), 100.0)


class Activity(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=200, help_text="e.g. Dry Ration Packing, Health Camp Vitals Check, Tree Sapling Planting")
    description = models.TextField(blank=True)
    required_skill = models.CharField(max_length=100, blank=True, help_text="e.g. Nursing, Teaching, Heavy Lifting, Driving")
    target_metric = models.CharField(max_length=150, blank=True, help_text="e.g. 2,000 Food Kits Distributed")

    class Meta:
        verbose_name_plural = "Activities"

    def __str__(self):
        return f"{self.title} ({self.campaign.title})"


class VolunteerAvailability(models.Model):
    DAY_CHOICES = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
        ('WEEKDAYS', 'All Weekdays (Mon-Fri)'),
        ('WEEKENDS', 'All Weekends (Sat-Sun)'),
    ]

    TIME_SLOT_CHOICES = [
        ('MORNING', 'Morning (08:00 AM - 12:00 PM)'),
        ('AFTERNOON', 'Afternoon (12:00 PM - 04:00 PM)'),
        ('EVENING', 'Evening (04:00 PM - 08:00 PM)'),
        ('FULL_DAY', 'Full Day (08:00 AM - 06:00 PM)'),
        ('ON_CALL', 'Emergency / On-Call 24x7'),
    ]

    volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.CharField(max_length=20, choices=DAY_CHOICES)
    time_slot = models.CharField(max_length=20, choices=TIME_SLOT_CHOICES, default='MORNING')
    notes = models.CharField(max_length=255, blank=True, help_text="e.g. Prefer North Delhi, Has 2-wheeler")

    class Meta:
        verbose_name_plural = "Volunteer Availabilities"

    def __str__(self):
        return f"{self.volunteer.user.get_full_name() or self.volunteer.user.username} - {self.get_day_of_week_display()} ({self.get_time_slot_display()})"


class Role(models.Model):
    name = models.CharField(max_length=100, help_text="Official Operational Role Name")
    code = models.CharField(max_length=30, unique=True, help_text="Short ID, e.g. FIRST_AID, MARSHALL, REG_DESK")
    description = models.TextField(help_text="Role summary and duties")
    key_responsibilities = models.TextField(help_text="Line items of standard operating procedures (SOP)")
    required_skills = models.CharField(max_length=200, blank=True, help_text="Comma-separated recommended skills")
    is_field_role = models.BooleanField(default=True, help_text="True if deployed on ground; False if back-office/IT")

    def __str__(self):
        return self.name


class Shift(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress / Active'),
        ('COMPLETED', 'Shift Completed'),
        ('CANCELLED', 'Shift Cancelled'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='shifts')
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True, related_name='shifts')
    title = models.CharField(max_length=200, help_text="e.g. Morning Medical Relief Drive - Camp 1")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reporting_location = models.TextField(help_text="Exact landmark or room where volunteers report")
    in_charge_name = models.CharField(max_length=100, default="Nodal Volunteer Officer")
    in_charge_contact = models.CharField(max_length=20, default="+91 9876543210")
    required_volunteers = models.PositiveIntegerField(default=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    special_instructions = models.TextField(blank=True, help_text="e.g. Wear NGO high-visibility jacket, bring photo ID, stay hydrated")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.title} on {self.date} ({self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')})"

    @property
    def duration_hours(self):
        dt_start = datetime.combine(date.today(), self.start_time)
        dt_end = datetime.combine(date.today(), self.end_time)
        delta = dt_end - dt_start
        hours = delta.total_seconds() / 3600.0
        return max(round(hours, 2), 0.5)

    @property
    def confirmed_count(self):
        return self.assignments.filter(status__in=['APPROVED', 'COMPLETED']).count()

    @property
    def slots_remaining(self):
        return max(0, self.required_volunteers - self.confirmed_count)

    @property
    def is_full(self):
        return self.slots_remaining <= 0


class ShiftAssignment(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Application Submitted (Pending Confirmation)'),
        ('APPROVED', 'Confirmed / Roster Assigned'),
        ('WAITLISTED', 'Waitlisted'),
        ('COMPLETED', 'Duty Successfully Completed'),
        ('CANCELLED', 'Cancelled / Withdrawn'),
        ('REJECTED', 'Application Not Approved'),
    ]

    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='assignments')
    volunteer = models.ForeignKey(VolunteerProfile, on_delete=models.CASCADE, related_name='shift_assignments')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPROVED')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='roster_allocations')
    admin_notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shift', 'volunteer')
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.volunteer.user.get_full_name() or self.volunteer.user.username} -> {self.shift.title} [{self.get_status_display()}]"


class ParticipationRecord(models.Model):
    ATTENDANCE_CHOICES = [
        ('PRESENT', 'Present on Ground'),
        ('ABSENT', 'Absent without Notice'),
        ('EXCUSED', 'Officially Excused / Pre-informed'),
        ('LATE', 'Reported Late (Completed partial duty)'),
    ]

    assignment = models.OneToOneField(ShiftAssignment, on_delete=models.CASCADE, related_name='participation_record')
    attendance_status = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES, default='PRESENT')
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    hours_logged = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text="Total credited volunteer service hours")
    performance_rating = models.PositiveSmallIntegerField(
        default=5,
        choices=[(1, '1 - Needs Improvement'), (2, '2 - Fair'), (3, '3 - Good Service'), (4, '4 - Very Good'), (5, '5 - Exemplary Seva')]
    )
    coordinator_remarks = models.TextField(blank=True, help_text="Official remarks by Shift In-Charge")
    volunteer_feedback = models.TextField(blank=True, help_text="Volunteer's ground experience or suggestions")
    
    # Official Digital Certificate ID (e.g. CERT-2026-X9Y1Z)
    certificate_code = models.CharField(max_length=40, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.certificate_code:
            # Auto-generate verifiable certificate number
            year = datetime.now().year
            rand_code = uuid.uuid4().hex[:8].upper()
            self.certificate_code = f"NGO-SEVA-{year}-{rand_code}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Record for {self.assignment.volunteer.user.username} on {self.assignment.shift.title} ({self.attendance_status})"


class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('NORMAL', 'General Circular'),
        ('IMPORTANT', 'Important Notice'),
        ('EMERGENCY', 'Aapda Emergency Mobilization'),
    ]

    title = models.CharField(max_length=200)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True, blank=True, related_name='announcements')
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='NORMAL')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.priority}] {self.title}"
