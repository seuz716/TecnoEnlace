from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from .views import (
    CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView,
    ProductoListView, ProductoClientListView, ProductoCreateView, ProductoUpdateView, ProductoDeleteView,
    buscar_productos, filtrar_productos, filtrar_productos_adm, ProductoDetailView
)

app_name = 'productos'

urlpatterns = [
    # Categorías (administración)
    path('categorias/', CategoriaListView.as_view(), name='categoria-list'),
    path('categorias/nueva/', CategoriaCreateView.as_view(), name='categoria-create'),
    path('categorias/editar/<int:pk>/', CategoriaUpdateView.as_view(), name='categoria-update'),
    path('categorias/eliminar/<int:pk>/', CategoriaDeleteView.as_view(), name='categoria-delete'),

    # Productos (administración)
    path('tienda/', ProductoListView.as_view(), name='producto-list'),
    path('productos/nuevo/', ProductoCreateView.as_view(), name='producto-create'),
    path('productos/editar/<int:pk>/', ProductoUpdateView.as_view(), name='producto-update'),
    path('productos/eliminar/<int:pk>/', ProductoDeleteView.as_view(), name='producto-delete'),
    path('buscar/', buscar_productos, name='buscar_productos'),
    path('filtrar/', filtrar_productos, name='filtrar_productos'),
    path('producto/<int:pk>/', ProductoDetailView.as_view(), name='producto-detail'),
    path('filtrarAdm/', filtrar_productos_adm, name='filtrar_productos_adm'),


    # Cliente: Listado de Productos con descripción resumida y "Agregar al Carrito"
    path('', ProductoClientListView.as_view(), name='producto_client_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
