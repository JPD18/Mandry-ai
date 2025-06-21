"""mandry_ai URL Configuration"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic import TemplateView
from django.http import HttpResponse
import os

def favicon_view(request):
    """Return empty response for favicon to prevent 404 errors"""
    return HttpResponse(status=204)  # No Content

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('visa.urls')),
    path('favicon.ico', favicon_view, name='favicon'),
]

# Serve static and media files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, serve static files through Django
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

# Serve frontend static files at root
urlpatterns += [
    re_path(r'^$', serve, {'document_root': settings.STATICFILES_DIRS[0], 'path': 'index.html'}),
    re_path(r'^(?!api/|admin/|static/|media/)(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0]}),
] 