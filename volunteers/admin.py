from django.contrib import admin
from .models import (
    VolunteerProfile, Campaign, Activity, VolunteerAvailability,
    Role, Shift, ShiftAssignment, ParticipationRecord, Announcement
)


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ('volunteer_id', 'get_full_name', 'phone', 'state', 'district', 'availability_status', 'verification_status', 'is_coordinator', 'created_at')
    list_filter = ('verification_status', 'availability_status', 'is_coordinator', 'state', 'blood_group')
    search_fields = ('volunteer_id', 'user__first_name', 'user__last_name', 'user__email', 'phone', 'skills')
    readonly_fields = ('volunteer_id', 'created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Volunteer Name'


class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 1


class ShiftInline(admin.TabularInline):
    model = Shift
    extra = 1
    fields = ('title', 'date', 'start_time', 'end_time', 'required_volunteers', 'status')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'sector', 'state', 'district', 'start_date', 'end_date', 'status', 'target_volunteers')
    list_filter = ('sector', 'status', 'state')
    search_fields = ('title', 'short_description', 'venue_address')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ActivityInline, ShiftInline]


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('title', 'campaign', 'date', 'start_time', 'end_time', 'required_volunteers', 'status', 'in_charge_name')
    list_filter = ('status', 'date', 'campaign')
    search_fields = ('title', 'reporting_location', 'in_charge_name')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_field_role', 'required_skills')
    search_fields = ('name', 'code', 'description')


@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'shift', 'role', 'status', 'assigned_at')
    list_filter = ('status', 'role', 'shift__campaign')
    search_fields = ('volunteer__user__first_name', 'volunteer__user__last_name', 'shift__title')


@admin.register(ParticipationRecord)
class ParticipationRecordAdmin(admin.ModelAdmin):
    list_display = ('certificate_code', 'assignment', 'attendance_status', 'hours_logged', 'performance_rating', 'created_at')
    list_filter = ('attendance_status', 'performance_rating')
    search_fields = ('certificate_code', 'assignment__volunteer__user__first_name', 'assignment__shift__title')
    readonly_fields = ('certificate_code', 'created_at', 'updated_at')


@admin.register(VolunteerAvailability)
class VolunteerAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'day_of_week', 'time_slot')
    list_filter = ('day_of_week', 'time_slot')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'campaign', 'priority', 'is_published', 'created_at')
    list_filter = ('priority', 'is_published')
    search_fields = ('title', 'message')
