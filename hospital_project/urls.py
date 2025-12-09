"""
URL configuration for hospital_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.views_create_admin import create_admin_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('departments/', include('departments.urls')),
    path('doctor/', include('doctors.urls')),
    path('patient/', include('patients.urls')),
    path('appointments/', include('appointments.urls')),
    path('pharmacy/', include('pharmacy.urls')),
    path('billing/', include('billing.urls')),
    path('adminpanel/', include('adminpanel.urls')),
    path("create-admin/", create_admin_view),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)
