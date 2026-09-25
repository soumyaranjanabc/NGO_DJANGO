from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public & Discovery
    path('', views.home, name='home'),
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/<slug:slug>/', views.campaign_detail, name='campaign_detail'),
    path('shifts/<int:shift_id>/', views.shift_detail, name='shift_detail'),
    path('verify-certificate/', views.verify_certificate, name='verify_certificate'),

    # Authentication & Registration
    path('register/', views.volunteer_register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Volunteer Self-Service Portal
    path('dashboard/', views.dashboard, name='dashboard'),
    path('volunteer/dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('volunteer/profile/edit/', views.volunteer_profile_edit, name='volunteer_profile_edit'),
    path('volunteer/availability/', views.manage_availability, name='manage_availability'),
    path('shifts/<int:shift_id>/apply/', views.apply_for_shift, name='apply_for_shift'),
    path('assignments/<int:assignment_id>/cancel/', views.cancel_shift_assignment, name='cancel_shift_assignment'),
    path('certificate/<int:record_id>/', views.volunteer_certificate, name='volunteer_certificate'),

    # Operations & Coordinator Command Center
    path('operations/', views.operations_dashboard, name='operations_dashboard'),
    path('operations/campaigns/new/', views.create_campaign, name='create_campaign'),
    path('operations/shifts/new/', views.create_shift, name='create_shift'),
    path('operations/campaigns/<int:campaign_id>/shifts/new/', views.create_shift, name='create_campaign_shift'),
    path('operations/shifts/<int:shift_id>/roster/', views.manage_shift_roster, name='manage_shift_roster'),
    path('operations/shifts/<int:shift_id>/attendance/', views.mark_shift_attendance, name='mark_shift_attendance'),
    path('operations/announcements/new/', views.create_announcement, name='create_announcement'),
    path('operations/export/volunteers/', views.export_volunteers_csv, name='export_volunteers_csv'),
    path('operations/export/attendance/', views.export_attendance_csv, name='export_attendance_csv'),
]
