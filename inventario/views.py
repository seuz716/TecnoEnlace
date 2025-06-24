from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import MovimientoInventario
from .forms import MovimientoInventarioForm

class MovimientoListView(ListView):
    model = MovimientoInventario
    template_name = 'inventario/lista.html'
    context_object_name = 'movimientos'
    paginate_by = 20  # puedes ajustar o eliminar

class MovimientoCreateView(CreateView):
    model = MovimientoInventario
    form_class = MovimientoInventarioForm
    template_name = 'inventario/formulario.html'
    success_url = reverse_lazy('inventario:lista')
