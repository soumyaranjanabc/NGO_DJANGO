import csv
from decimal import Decimal
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.db.models import Sum, Count, Q
from django.utils import timezone

from .models import (
    VolunteerProfile, Campaign, Activity, VolunteerAvailability,
    Role, Shift, ShiftAssignment, ParticipationRecord, Announcement
)
from .forms import (
    VolunteerRegistrationForm, VolunteerProfileUpdateForm, AvailabilityForm,
    CampaignForm, ShiftForm, RoleAssignmentForm, AttendanceMarkForm,
    VolunteerFeedbackForm, AnnouncementForm
)


def is_coordinator_check(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return hasattr(user, 'volunteer_profile') and user.volunteer_profile.is_coordinator


def home(request):
    """
    Public Landing Page with Government of India Portal Aesthetic.
    Highlights national statistics, active campaigns, announcements ticker, and pledge.
    """
    # Key National Mobilization Statistics
    total_volunteers = VolunteerProfile.objects.filter(verification_status='VERIFIED').count()
    active_campaigns_count = Campaign.objects.filter(status='ACTIVE').count()
    total_shifts_conducted = Shift.objects.filter(status__in=['COMPLETED', 'IN_PROGRESS', 'SCHEDULED']).count()
    
    total_hours_aggregated = ParticipationRecord.objects.filter(
        attendance_status__in=['PRESENT', 'LATE']
    ).aggregate(total=Sum('hours_logged'))['total']
    total_hours_served = round(float(total_hours_aggregated or 0), 1)

    districts_covered = Campaign.objects.values('district').distinct().count()

    # Active Campaigns
    featured_campaigns = Campaign.objects.filter(status='ACTIVE').order_by('-start_date')[:6]
    
    # Recent Circulars
    announcements = Announcement.objects.filter(is_published=True).order_by('-created_at')[:4]

    context = {
        'total_volunteers': total_volunteers,
        'active_campaigns_count': active_campaigns_count,
        'total_shifts_conducted': total_shifts_conducted,
        'total_hours_served': total_hours_served,
        'districts_covered': max(districts_covered, 1),
        'featured_campaigns': featured_campaigns,
        'announcements': announcements,
    }
    return render(request, 'volunteers/home.html', context)


def campaign_list(request):
    """
    Searchable and filterable directory of NGO campaigns.
    """
    query = request.GET.get('q', '').strip()
    sector = request.GET.get('sector', '').strip()
    status = request.GET.get('status', '').strip()
    state = request.GET.get('state', '').strip()

    campaigns = Campaign.objects.all().order_by('-start_date')

    if query:
        campaigns = campaigns.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(district__icontains=query) |
            Q(state__icontains=query)
        )
    if sector:
        campaigns = campaigns.filter(sector=sector)
    if status:
        campaigns = campaigns.filter(status=status)
    if state:
        campaigns = campaigns.filter(state__icontains=state)

    sectors = Campaign.SECTOR_CHOICES
    statuses = Campaign.STATUS_CHOICES

    context = {
        'campaigns': campaigns,
        'query': query,
        'selected_sector': sector,
        'selected_status': status,
        'selected_state': state,
        'sectors': sectors,
        'statuses': statuses,
    }
    return render(request, 'volunteers/campaign_list.html', context)


def campaign_detail(request, slug):
    """
    Detailed campaign overview: objectives, field venue, active activities,
    and scheduled shifts with volunteer enrollment status.
    """
    campaign = get_object_or_404(Campaign, slug=slug)
    activities = campaign.activities.all()
    shifts = campaign.shifts.all().order_by('date', 'start_time')

    # If logged in, check which shifts the volunteer has already applied to
    user_enrolled_shift_ids = []
    if request.user.is_authenticated and hasattr(request.user, 'volunteer_profile'):
        user_enrolled_shift_ids = list(
            ShiftAssignment.objects.filter(
                volunteer=request.user.volunteer_profile,
                shift__campaign=campaign
            ).values_list('shift_id', flat=True)
        )

    context = {
        'campaign': campaign,
        'activities': activities,
        'shifts': shifts,
        'user_enrolled_shift_ids': user_enrolled_shift_ids,
    }
    return render(request, 'volunteers/campaign_detail.html', context)


def shift_detail(request, shift_id):
    """
    Shift briefing: location, reporting instructions, supervisor contact,
    roles available, and registration button.
    """
    shift = get_object_or_404(Shift, id=shift_id)
    available_roles = Role.objects.all()
    user_assignment = None

    if request.user.is_authenticated and hasattr(request.user, 'volunteer_profile'):
        user_assignment = ShiftAssignment.objects.filter(
            shift=shift,
            volunteer=request.user.volunteer_profile
        ).first()

    context = {
        'shift': shift,
        'available_roles': available_roles,
        'user_assignment': user_assignment,
    }
    return render(request, 'volunteers/shift_detail.html', context)


def volunteer_register(request):
    """
    Volunteer registration creating User and official VolunteerProfile.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = VolunteerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )

            profile = form.save(commit=False)
            profile.user = user
            profile.save()

            login(request, user)
            messages.success(request, f"Namaste {user.first_name}! You have been registered successfully as Volunteer ID: {profile.volunteer_id}")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors indicated below.")
    else:
        form = VolunteerRegistrationForm()

    return render(request, 'volunteers/register.html', {'form': form})


@login_required
def dashboard(request):
    """
    Intelligent routing to Coordinator Operations Dashboard or Volunteer Self-Service Dashboard.
    """
    if is_coordinator_check(request.user) and request.GET.get('view') != 'volunteer':
        return redirect('operations_dashboard')
    return redirect('volunteer_dashboard')


@login_required
def volunteer_dashboard(request):
    """
    Volunteer Self-Service Portal:
    - Official Seva Identity Badge & hours served.
    - Assigned / Upcoming Shifts.
    - Past service history & Certificate downloads.
    - Quick availability toggle.
    """
    if not hasattr(request.user, 'volunteer_profile'):
        messages.warning(request, "Please create a volunteer profile to access the volunteer portal.")
        # Create standard profile if missing (e.g. for superusers)
        profile = VolunteerProfile.objects.create(
            user=request.user,
            phone="9876543210",
            state="Delhi",
            district="Central",
            skills="General Volunteer, Coordination",
            is_coordinator=request.user.is_staff
        )
    else:
        profile = request.user.volunteer_profile

    # Quick availability status update
    if request.method == 'POST' and 'update_availability_status' in request.POST:
        new_status = request.POST.get('availability_status')
        if new_status in dict(VolunteerProfile.AVAILABILITY_CHOICES):
            profile.availability_status = new_status
            profile.save()
            messages.success(request, f"Your availability status is now updated to: {profile.get_availability_status_display()}")
            return redirect('volunteer_dashboard')

    # Upcoming Shifts
    today = timezone.localdate()
    upcoming_assignments = ShiftAssignment.objects.filter(
        volunteer=profile,
        shift__date__gte=today,
        status__in=['APPLIED', 'APPROVED']
    ).select_related('shift', 'shift__campaign', 'role').order_by('shift__date', 'shift__start_time')

    # Past Completed Participation Records
    past_records = ParticipationRecord.objects.filter(
        assignment__volunteer=profile
    ).select_related('assignment__shift', 'assignment__shift__campaign', 'assignment__role').order_by('-created_at')

    # Recommended upcoming shifts in their state/area
    open_shifts = Shift.objects.filter(
        date__gte=today,
        status='SCHEDULED'
    ).exclude(
        assignments__volunteer=profile
    ).select_related('campaign').order_by('date')[:4]

    availabilities = profile.availabilities.all()

    context = {
        'profile': profile,
        'upcoming_assignments': upcoming_assignments,
        'past_records': past_records,
        'open_shifts': open_shifts,
        'availabilities': availabilities,
    }
    return render(request, 'volunteers/volunteer_dashboard.html', context)


@login_required
def volunteer_profile_edit(request):
    """
    Edit volunteer profile, phone, address, skills, and profile photo.
    """
    profile = get_object_or_404(VolunteerProfile, user=request.user)

    if request.method == 'POST':
        form = VolunteerProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            form.save()
            messages.success(request, "Your volunteer profile has been successfully updated.")
            return redirect('volunteer_dashboard')
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = VolunteerProfileUpdateForm(instance=profile, initial=initial)

    return render(request, 'volunteers/profile_edit.html', {'form': form, 'profile': profile})


@login_required
def manage_availability(request):
    """
    Manage recurring weekly availability slots (e.g. Saturdays Morning, Weekdays Evening).
    """
    profile = get_object_or_404(VolunteerProfile, user=request.user)
    availabilities = profile.availabilities.all()

    if request.method == 'POST':
        if 'add_slot' in request.POST:
            form = AvailabilityForm(request.POST)
            if form.is_valid():
                slot = form.save(commit=False)
                slot.volunteer = profile
                slot.save()
                messages.success(request, "Availability slot added successfully.")
                return redirect('manage_availability')
        elif 'delete_slot' in request.POST:
            slot_id = request.POST.get('slot_id')
            profile.availabilities.filter(id=slot_id).delete()
            messages.info(request, "Availability slot removed.")
            return redirect('manage_availability')
    else:
        form = AvailabilityForm()

    context = {
        'profile': profile,
        'availabilities': availabilities,
        'form': form,
    }
    return render(request, 'volunteers/manage_availability.html', context)


@login_required
def apply_for_shift(request, shift_id):
    """
    Volunteer applies to enroll in a specific shift.
    """
    shift = get_object_or_404(Shift, id=shift_id)
    profile = get_object_or_404(VolunteerProfile, user=request.user)

    existing = ShiftAssignment.objects.filter(shift=shift, volunteer=profile).first()
    if existing:
        messages.info(request, f"You are already registered for this shift with status: {existing.get_status_display()}")
        return redirect('shift_detail', shift_id=shift.id)

    role_id = request.POST.get('role_id')
    role = None
    if role_id:
        role = Role.objects.filter(id=role_id).first()

    # Determine status based on slot availability
    status = 'APPROVED'
    if shift.is_full:
        status = 'WAITLISTED'

    ShiftAssignment.objects.create(
        shift=shift,
        volunteer=profile,
        role=role,
        status=status,
        admin_notes="Self-enrolled via Volunteer Portal"
    )

    if status == 'APPROVED':
        messages.success(request, f"Congratulations! You have been confirmed for '{shift.title}' on {shift.date}.")
    else:
        messages.warning(request, f"Shift quota reached. You have been placed on the WAITLIST for '{shift.title}'. We will notify you if a slot opens.")

    return redirect('volunteer_dashboard')


@login_required
def cancel_shift_assignment(request, assignment_id):
    """
    Volunteer withdraws or cancels an assigned shift.
    """
    assignment = get_object_or_404(ShiftAssignment, id=assignment_id, volunteer__user=request.user)
    
    if request.method == 'POST':
        assignment.status = 'CANCELLED'
        assignment.save()
        messages.info(request, f"Your registration for '{assignment.shift.title}' has been cancelled.")
        return redirect('volunteer_dashboard')

    return render(request, 'volunteers/cancel_assignment_confirm.html', {'assignment': assignment})


@login_required
def volunteer_certificate(request, record_id):
    """
    Printable Official Digital Certificate of Appreciation.
    Features Government of India / National NGO Seal, Verification Code, and Signature.
    """
    record = get_object_or_404(ParticipationRecord, id=record_id)
    
    # Ensure only owner or coordinator/staff can view
    if record.assignment.volunteer.user != request.user and not is_coordinator_check(request.user):
        raise Http404("You do not have permission to view this certificate.")

    context = {
        'record': record,
        'volunteer': record.assignment.volunteer,
        'shift': record.assignment.shift,
        'campaign': record.assignment.shift.campaign,
        'issue_date': record.created_at.strftime('%d %B, %Y'),
    }
    return render(request, 'volunteers/certificate.html', context)


def verify_certificate(request):
    """
    Public verification portal for Certificate of Appreciation.
    """
    cert_code = request.GET.get('code', '').strip().upper()
    record = None
    searched = False

    if cert_code:
        searched = True
        record = ParticipationRecord.objects.filter(certificate_code=cert_code).first()

    context = {
        'cert_code': cert_code,
        'record': record,
        'searched': searched,
    }
    return render(request, 'volunteers/verify_certificate.html', context)


# ============================================================================
# OPERATIONS & COORDINATOR MANAGEMENT VIEWS
# ============================================================================

@login_required
@user_passes_test(is_coordinator_check)
def operations_dashboard(request):
    """
    High-level Operations Command Center for NGO Coordinators and Officers.
    Live mobilization KPIs, upcoming shifts, quick attendance links.
    """
    total_volunteers = VolunteerProfile.objects.count()
    verified_volunteers = VolunteerProfile.objects.filter(verification_status='VERIFIED').count()
    pending_volunteers = VolunteerProfile.objects.filter(verification_status='PENDING').count()
    
    active_campaigns = Campaign.objects.filter(status='ACTIVE')
    
    today = timezone.localdate()
    upcoming_shifts = Shift.objects.filter(date__gte=today).order_by('date', 'start_time')[:10]
    shifts_needing_attendance = Shift.objects.filter(date__lte=today, status__in=['SCHEDULED', 'IN_PROGRESS']).order_by('-date')[:5]

    total_hours_aggregated = ParticipationRecord.objects.aggregate(total=Sum('hours_logged'))['total']
    total_hours = round(float(total_hours_aggregated or 0), 1)

    # Sector breakdown
    sector_stats = Campaign.objects.values('sector').annotate(count=Count('id')).order_by('-count')

    context = {
        'total_volunteers': total_volunteers,
        'verified_volunteers': verified_volunteers,
        'pending_volunteers': pending_volunteers,
        'active_campaigns': active_campaigns,
        'upcoming_shifts': upcoming_shifts,
        'shifts_needing_attendance': shifts_needing_attendance,
        'total_hours': total_hours,
        'sector_stats': sector_stats,
    }
    return render(request, 'volunteers/operations_dashboard.html', context)


@login_required
@user_passes_test(is_coordinator_check)
def create_campaign(request):
    """
    Coordinator view to launch a new NGO campaign.
    """
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.lead_coordinator = request.user
            campaign.save()
            messages.success(request, f"Campaign '{campaign.title}' initialized successfully.")
            return redirect('campaign_detail', slug=campaign.slug)
    else:
        form = CampaignForm()

    return render(request, 'volunteers/campaign_form.html', {'form': form, 'title': 'Create New National Campaign'})


@login_required
@user_passes_test(is_coordinator_check)
def create_shift(request, campaign_id=None):
    """
    Coordinator schedules an operational shift for a campaign.
    """
    campaign = None
    if campaign_id:
        campaign = get_object_or_404(Campaign, id=campaign_id)

    if request.method == 'POST':
        form = ShiftForm(request.POST)
        if form.is_valid():
            shift = form.save()
            messages.success(request, f"Shift '{shift.title}' scheduled for {shift.date}.")
            return redirect('shift_detail', shift_id=shift.id)
    else:
        initial = {}
        if campaign:
            initial['campaign'] = campaign
        form = ShiftForm(initial=initial)

    return render(request, 'volunteers/shift_form.html', {'form': form, 'campaign': campaign})


@login_required
@user_passes_test(is_coordinator_check)
def manage_shift_roster(request, shift_id):
    """
    Shift Roster Controller:
    - View volunteers who applied.
    - Assign operational roles (Field Marshall, Medic, Logistics, etc.).
    - Confirm / Approve / Waitlist volunteers.
    """
    shift = get_object_or_404(Shift, id=shift_id)
    assignments = shift.assignments.select_related('volunteer', 'volunteer__user', 'role').all()
    roles = Role.objects.all()

    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')
        action = request.POST.get('action')
        role_id = request.POST.get('role_id')

        assignment = get_object_or_404(ShiftAssignment, id=assignment_id, shift=shift)

        if action == 'approve':
            assignment.status = 'APPROVED'
        elif action == 'waitlist':
            assignment.status = 'WAITLISTED'
        elif action == 'cancel':
            assignment.status = 'CANCELLED'

        if role_id:
            role = Role.objects.filter(id=role_id).first()
            assignment.role = role

        assignment.assigned_by = request.user
        assignment.save()
        messages.success(request, f"Roster updated for {assignment.volunteer.user.get_full_name() or assignment.volunteer.user.username}.")
        return redirect('manage_shift_roster', shift_id=shift.id)

    context = {
        'shift': shift,
        'assignments': assignments,
        'roles': roles,
    }
    return render(request, 'volunteers/manage_shift_roster.html', context)


@login_required
@user_passes_test(is_coordinator_check)
def mark_shift_attendance(request, shift_id):
    """
    Batch Attendance and Participation Sheet for Coordinators:
    Mark Present/Absent, credit service hours, rate performance, and issue certificates.
    """
    shift = get_object_or_404(Shift, id=shift_id)
    assignments = shift.assignments.filter(status__in=['APPROVED', 'COMPLETED']).select_related('volunteer__user', 'role', 'participation_record')

    if request.method == 'POST':
        # Batch save attendance records
        updated_count = 0
        for assignment in assignments:
            status_key = f"status_{assignment.id}"
            hours_key = f"hours_{assignment.id}"
            rating_key = f"rating_{assignment.id}"
            remarks_key = f"remarks_{assignment.id}"

            if status_key in request.POST:
                status_val = request.POST.get(status_key)
                try:
                    hours_val = Decimal(request.POST.get(hours_key, shift.duration_hours))
                except (ValueError, TypeError):
                    hours_val = Decimal(shift.duration_hours)

                rating_val = int(request.POST.get(rating_key, 5))
                remarks_val = request.POST.get(remarks_key, '')

                record, created = ParticipationRecord.objects.get_or_create(
                    assignment=assignment,
                    defaults={
                        'attendance_status': status_val,
                        'hours_logged': hours_val,
                        'performance_rating': rating_val,
                        'coordinator_remarks': remarks_val,
                    }
                )
                if not created:
                    record.attendance_status = status_val
                    record.hours_logged = hours_val
                    record.performance_rating = rating_val
                    record.coordinator_remarks = remarks_val
                    record.save()

                if status_val == 'PRESENT':
                    assignment.status = 'COMPLETED'
                    assignment.save()

                updated_count += 1

        # Update shift status to COMPLETED
        shift.status = 'COMPLETED'
        shift.save()

        messages.success(request, f"Attendance finalized successfully for {updated_count} volunteers. Service hours and certificates generated!")
        return redirect('operations_dashboard')

    context = {
        'shift': shift,
        'assignments': assignments,
        'default_hours': shift.duration_hours,
    }
    return render(request, 'volunteers/mark_attendance.html', context)


@login_required
@user_passes_test(is_coordinator_check)
def create_announcement(request):
    """
    Publish official notice or emergency mobilization alert.
    """
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save()
            messages.success(request, f"Notice '{announcement.title}' published successfully.")
            return redirect('operations_dashboard')
    else:
        form = AnnouncementForm()

    return render(request, 'volunteers/announcement_form.html', {'form': form})


@login_required
@user_passes_test(is_coordinator_check)
def export_volunteers_csv(request):
    """
    Export full directory of volunteers to CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="NGO_Volunteers_Roster_{date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Volunteer ID', 'Full Name', 'Email', 'Phone', 'State', 'District',
        'Blood Group', 'Occupation', 'Skills', 'Availability Status',
        'Verification Status', 'Total Hours Served', 'Registered Date'
    ])

    volunteers = VolunteerProfile.objects.select_related('user').all()
    for v in volunteers:
        writer.writerow([
            v.volunteer_id,
            v.user.get_full_name() or v.user.username,
            v.user.email,
            v.phone,
            v.state,
            v.district,
            v.blood_group,
            v.occupation,
            v.skills,
            v.get_availability_status_display(),
            v.get_verification_status_display(),
            v.total_hours_served,
            v.created_at.strftime('%Y-%m-%d')
        ])

    return response


@login_required
@user_passes_test(is_coordinator_check)
def export_attendance_csv(request):
    """
    Export all participation records to CSV for auditing.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="NGO_Participation_Log_{date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Certificate Code', 'Volunteer ID', 'Volunteer Name', 'Campaign',
        'Shift Title', 'Shift Date', 'Role', 'Attendance Status',
        'Hours Logged', 'Rating (1-5)', 'Coordinator Remarks', 'Verified At'
    ])

    records = ParticipationRecord.objects.select_related(
        'assignment__volunteer__user',
        'assignment__shift__campaign',
        'assignment__role'
    ).all()

    for r in records:
        writer.writerow([
            r.certificate_code,
            r.assignment.volunteer.volunteer_id,
            r.assignment.volunteer.user.get_full_name() or r.assignment.volunteer.user.username,
            r.assignment.shift.campaign.title,
            r.assignment.shift.title,
            r.assignment.shift.date,
            r.assignment.role.name if r.assignment.role else 'General Volunteer',
            r.get_attendance_status_display(),
            r.hours_logged,
            r.performance_rating,
            r.coordinator_remarks,
            r.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response
