from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from tienda import views  # ✅ SOLO esto, no uses `from . import views` en este archivo

from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', RedirectView.as_view(url='/accounts/login/')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('productos.urls', namespace='productos')),
    path('cart/', include('cart.urls')),
    path('politica-privacidad/', views.politica_privacidad, name='politica-privacidad'),
    path('contacto/', views.contacto, name='contacto'),
    path('terminos-servicio/', views.terminos_servicio, name='terminos-servicio'),

]

# Handlers de errores
handler404 = 'tienda.views.custom_404'
handler500 = 'tienda.views.custom_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path('404/', views.custom_404),
        path('500/', views.custom_500),
    ]
