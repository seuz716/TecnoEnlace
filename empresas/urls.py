from django.urls import path
from . import views

app_name = 'empresa'

urlpatterns = [
    path('redirigir-empresa/', views.redirigir_empresa, name='redirigir-empresa'),
    path('mi-empresa/', views.EmpresaDetailView.as_view(), name='empresa-detalle'),
    path('mi-empresa/editar/', views.EmpresaUpdateView.as_view(), name='empresa-editar'),
    path('', views.EmpresaCreateView.as_view(), name='empresa-crear'),
]
