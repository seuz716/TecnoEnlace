from django.urls import path
from .views import (
    CartListView, CartDetailView, CartCreateView, CartUpdateView, CartDeleteView,
    add_to_cart, enviar_whatsapp, cart_count, PedidoCreateView, get_cart_count
)

app_name = 'cart'

urlpatterns = [
    path('', CartListView.as_view(), name='list'),
    path('detail/<int:pk>/', CartDetailView.as_view(), name='detail'),
    path('add/<int:producto_id>/', add_to_cart, name='add'),
    path('update/<int:pk>/', CartUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', CartDeleteView.as_view(), name='delete'),
    path('enviar/', enviar_whatsapp, name='enviar'),
    path('pedido/', PedidoCreateView.as_view(), name='pedido_create'),
    path('count/', cart_count, name='count'),
    path('cart/count/', get_cart_count, name='cart-count'),
]
