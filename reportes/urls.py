from django.urls import path
from . import views
from .views import ValoracionInventarioView, RentabilidadProductosView, CMVView, CMVMensualView, InventarioActualView, ProductosBajoStockView, HistorialProductoView

app_name = 'reportes'

urlpatterns = [
    path('kardex/<int:producto_id>/', views.KardexProductoView.as_view(), name='kardex'),
    path('valoracion/', ValoracionInventarioView.as_view(), name='valoracion_inventario'),
    path('rentabilidad/', RentabilidadProductosView.as_view(), name='rentabilidad'),
    path('', CMVView.as_view(), name='cmv'),
    path('cmv/', CMVMensualView.as_view(), name='cmv_mensual'),
    path('inventario/', InventarioActualView.as_view(), name='inventario_actual'),
    path('bajo-stock/', ProductosBajoStockView.as_view(), name='productos_bajo_stock'),
    path('historial/<int:producto_id>/', HistorialProductoView.as_view(), name='historial_producto'),
]



