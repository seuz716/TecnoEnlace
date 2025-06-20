from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from .models import Categoria, Producto
from .forms import CategoriaForm, ProductoForm


# ----------------------
# VISTAS PARA CATEGORÍA
# ----------------------

class CategoriaListView(LoginRequiredMixin,ListView):
    model = Categoria
    template_name = 'productos/categoria_list.html'
    context_object_name = 'categorias'


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'productos/categoria_form.html'
    success_url = reverse_lazy('productos:categoria-list')


class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'productos/categoria_form.html'
    success_url = reverse_lazy('productos:categoria-list')


class CategoriaDeleteView(LoginRequiredMixin,DeleteView):
    model = Categoria
    template_name = 'productos/categoria_confirm_delete.html'
    success_url = reverse_lazy('productos:categoria-list')


# --------------------
# VISTAS PARA PRODUCTO
# --------------------

class ProductoListView(ListView):
    model = Producto
    template_name = 'productos/producto_list.html'
    context_object_name = 'productos'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('categoria')
        categoria_slug = self.request.GET.get('categoria', '').strip()
        price_filter = self.request.GET.get('priceFilter', '').strip()

        if categoria_slug:
            queryset = queryset.filter(categoria__slug=categoria_slug)
        if price_filter == 'asc':
            queryset = queryset.order_by('precio')
        elif price_filter == 'desc':
            queryset = queryset.order_by('-precio')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all().only('nombre', 'slug')
        return context


class ProductoCreateView(LoginRequiredMixin,CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('productos:producto-list')


class ProductoUpdateView(LoginRequiredMixin,UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('productos:producto-list')


class ProductoDeleteView(LoginRequiredMixin,DeleteView):
    model = Producto
    template_name = 'productos/producto_confirm_delete.html'
    success_url = reverse_lazy('productos:producto-list')


class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'productos/producto_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto = self.object

        # Obtener hasta 4 productos aleatorios de la misma categoría (excluyendo el actual)
        context['related_products'] = Producto.objects.filter(
            categoria=producto.categoria,
            disponible=True
        ).exclude(id=producto.id).order_by('?')[:4]

        return context


class ProductoClientListView(ListView):
    model = Producto
    template_name = 'productos/producto_client_list.html'
    context_object_name = 'productos'

    def get_queryset(self):
        queryset = Producto.objects.filter(disponible=True).select_related('categoria')
        categoria_slug = self.request.GET.get('categoria', '').strip()
        price_filter = self.request.GET.get('priceFilter', '').strip()

        if categoria_slug:
            queryset = queryset.filter(categoria__slug=categoria_slug)
        if price_filter == 'asc':
            queryset = queryset.order_by('precio')
        elif price_filter == 'desc':
            queryset = queryset.order_by('-precio')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all().only('nombre', 'slug')
        return context


# -----------------------------------------
# VISTAS AJAX Y BÚSQUEDA/FILTROS PARCIALES
# -----------------------------------------

@require_GET
@csrf_protect
def buscar_productos(request):
    categoria_slug = request.GET.get('categoria', '').strip()
    price_filter = request.GET.get('priceFilter', '').strip()
    productos = Producto.objects.select_related('categoria')

    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)
    if price_filter == 'asc':
        productos = productos.order_by('precio')
    elif price_filter == 'desc':
        productos = productos.order_by('-precio')

    html = render_to_string('productos/_product_grid.html', {'productos': productos}, request=request)
    return JsonResponse({'html': html})


@require_GET
@csrf_protect
def filtrar_productos(request):
    try:
        productos = Producto.objects.all().select_related('categoria')
        search_query = request.GET.get('search', '').strip()

        if search_query:
            productos = productos.filter(
                Q(nombre__icontains=search_query) |
                Q(descripcion__icontains=search_query) |
                Q(categoria__nombre__icontains=search_query)
            )

        html = render_to_string('productos/_product_grid.html', {'productos': productos}, request=request)
        return JsonResponse({'html': html})
    except Exception as e:
        # Evita exponer errores internos en producción. Usa logging si es necesario.
        return HttpResponseServerError("Ocurrió un error al filtrar los productos.")


@require_GET
@csrf_protect
def filtrar_productos_adm(request):
    categoria_slug = request.GET.get('categoria', '').strip()
    price_filter = request.GET.get('priceFilter', '').strip()
    productos = Producto.objects.all().select_related('categoria')

    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)
    if price_filter == 'asc':
        productos = productos.order_by('precio')
    elif price_filter == 'desc':
        productos = productos.order_by('-precio')

    html = render_to_string('productos/_product_gridAdm.html', {'productos': productos}, request=request)
    return JsonResponse({'html': html})
