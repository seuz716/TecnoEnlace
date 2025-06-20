from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db import transaction

from .models import Carrito, Pedido
from productos.models import Producto


def get_session_key(request):
    """
    Retorna el session key de la request; si no existe, lo crea.
    """
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def construir_mensaje_pedido(carrito_items, pedido=None):
    mensaje = "Pedido:\n"
    total = 0
    for item in carrito_items:
        subtotal = item.producto.precio * item.cantidad
        mensaje += f"{item.producto.nombre} x {item.cantidad} - ${subtotal}\n"
        total += subtotal
    mensaje += f"Total: ${total}\n"
    if pedido is not None:
        mensaje += (
            f"Cliente: {pedido.nombre}\n"
            f"Teléfono: {pedido.telefono}\n"
            f"Dirección: {pedido.direccion}\n"
            f"Correo: {pedido.correo}\n"
        )
        if pedido.necesita_factura:
            mensaje += f"Factura requerida. Documento: {pedido.numero_documento}\n"
    return mensaje


def enviar_correo_pedido(pedido, mensaje):
    subject = "Confirmación de Pedido"
    from_email = "ceanabad@gmail.com"
    recipient_list = [pedido.correo]
    send_mail(subject, mensaje, from_email, recipient_list, fail_silently=False)


def construir_url_whatsapp(mensaje):
    params = urlencode({"text": mensaje})
    whatsapp_url = f"https://api.whatsapp.com/send?phone=+573166710912&{params}"
    return whatsapp_url


# --- Función para agregar productos al carrito ---
def add_to_cart(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    session_key = get_session_key(request)
    cantidad = int(request.POST.get('cantidad', 1))
    item, created = Carrito.objects.get_or_create(
        session_key=session_key,
        producto=producto,
        defaults={'cantidad': cantidad}
    )
    if not created:
        item.cantidad += cantidad
        item.save()

    cart_count = Carrito.objects.filter(session_key=session_key).count()

    # Responde en JSON si es solicitud AJAX
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart_count})
    else:
        return redirect('cart:list')


# --- Vista para mostrar el resumen del carrito ---
class CartListView(ListView):
    model = Carrito
    template_name = 'cart/cart_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        session_key = get_session_key(self.request)
        return Carrito.objects.filter(session_key=session_key)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = sum(item.producto.precio * item.cantidad for item in context['items'])
        context['total'] = total
        return context


class CartDetailView(DetailView):
    model = Carrito
    template_name = 'cart/cart_detail.html'
    context_object_name = 'item'


class CartCreateView(CreateView):
    model = Carrito
    template_name = 'cart/cart_form.html'
    fields = ['producto', 'cantidad']

    def form_valid(self, form):
        session_key = get_session_key(self.request)
        form.instance.session_key = session_key
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cart:list')


class CartUpdateView(UpdateView):
    model = Carrito
    template_name = 'cart/cart_form.html'
    fields = ['cantidad']

    def get_success_url(self):
        return reverse_lazy('cart:list')


class CartDeleteView(DeleteView):
    model = Carrito
    template_name = 'cart/cart_confirm_delete.html'
    success_url = reverse_lazy('cart:list')


def cart_count(request):
    session_key = get_session_key(request)
    count = Carrito.objects.filter(session_key=session_key).count()
    return JsonResponse({'count': count})


# --- Vista para procesar el pedido (checkout) ---
from django.shortcuts import render  # asegúrate de que esté importado

class PedidoCreateView(CreateView):
    model = Pedido
    template_name = 'cart/pedido_form.html'
    fields = [
        'nombre', 'telefono', 'direccion', 'detalles',
        'correo', 'necesita_factura', 'numero_documento', 'archivo_rut'
    ]

    def form_valid(self, form):
        with transaction.atomic():
            session_key = get_session_key(self.request)
            form.instance.session_key = session_key
            self.object = form.save()

            carrito_items = Carrito.objects.filter(session_key=session_key)
            mensaje = construir_mensaje_pedido(carrito_items, self.object)

            # Envía el correo de confirmación
            enviar_correo_pedido(self.object, mensaje)

            # Construye la URL de WhatsApp con el mensaje prellenado
            whatsapp_url = construir_url_whatsapp(mensaje)

            # Vacía el carrito tras crear el pedido
            carrito_items.delete()

        # Aquí puedes redirigir a WhatsApp o mostrar un mensaje de éxito en la misma página
        return redirect(whatsapp_url)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {
            'form': form,
            'pedido_exitoso': False
        })

    def get_success_url(self):
        return reverse_lazy('cart:list')
        


# --- Vista para enviar pedido a WhatsApp (opcional) ---
def enviar_whatsapp(request):
    session_key = get_session_key(request)
    carrito_items = Carrito.objects.filter(session_key=session_key)
    if not carrito_items.exists():
        return redirect('cart:list')
    
    mensaje = construir_mensaje_pedido(carrito_items)
    whatsapp_url = construir_url_whatsapp(mensaje)
    return redirect(whatsapp_url)


def get_cart_count(request):
    session_key = get_session_key(request)
    cart_count = Carrito.objects.filter(session_key=session_key).count()
    return JsonResponse({'cart_count': cart_count})
