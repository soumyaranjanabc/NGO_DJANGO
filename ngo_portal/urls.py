"""
URL configuration for ngo_portal project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customize Django Admin Header for Government of India / NGO portal aesthetic
admin.site.site_header = "राष्ट्रीय सेवा सेतु | NGO Operations Administration"
admin.site.site_title = "National Volunteer Operations Portal Admin"
admin.site.index_title = "Seva Operations Command & Registry"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('volunteers.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
