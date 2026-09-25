from datetime import datetime
from .models import Announcement

def ngo_context(request):
    """
    Global context processor injecting portal branding, emergency contacts,
    and latest announcements for the government-style ticker.
    """
    announcements = Announcement.objects.filter(is_published=True)[:5]
    
    is_coordinator = False
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            is_coordinator = True
        elif hasattr(request.user, 'volunteer_profile') and request.user.volunteer_profile.is_coordinator:
            is_coordinator = True

    return {
        'NGO_PORTAL_NAME': 'राष्ट्रीय सेवा सेतु (Rashtriya Seva Setu)',
        'NGO_SUBTITLE': 'National Volunteer Operations & Humanitarian Mobilization Network',
        'NGO_AFFILIATION': 'Recognized Voluntary Action Network • Registered Public Trust / NGO',
        'HELPLINE_PRIMARY': '1800-11-2026 (Toll-Free 24x7)',
        'HELPLINE_SECONDARY': '+91 11 2338 9000',
        'HELPLINE_EMAIL': 'seva.operations@gov-ngo.org.in',
        'ticker_announcements': announcements,
        'current_year': datetime.now().year,
        'user_is_coordinator': is_coordinator,
    }
