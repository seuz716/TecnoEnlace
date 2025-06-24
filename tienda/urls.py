from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from tienda import views  

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
    
    # Tus apps
    path('', include('productos.urls', namespace='productos')),
    path('cart/', include('cart.urls')),
    path('inventario/', include('inventario.urls', namespace='inventario')),
    path('empresa/', include('empresas.urls', namespace='empresas')),
    path("ia/", include("ia.urls")),
    path('reportes/', include('reportes.urls', namespace='reportes')),


    # Páginas legales y contacto
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
