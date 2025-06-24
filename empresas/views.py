from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, UpdateView, CreateView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Empresa
from .forms import EmpresaForm

# Vista redirección después del login
@login_required
def redirigir_empresa(request):
    if hasattr(request.user, 'empresa'):
        return redirect('empresa:empresa-detalle')
    else:
        return redirect('empresa:empresa-crear')

# Mixin que restringe acceso a la empresa del usuario
class EmpresaAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'empresa')

    def handle_no_permission(self):
        return redirect('empresa:empresa-crear')

# Vista detalle (solo accede si ya tiene empresa)
class EmpresaDetailView(EmpresaAccessMixin, DetailView):
    model = Empresa
    template_name = 'empresa/detalle.html'

    def get_object(self, queryset=None):
        return self.request.user.empresa

# Vista actualizar empresa
class EmpresaUpdateView(EmpresaAccessMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'empresa/formulario.html'
    success_url = '/empresa/mi-empresa/'

    def get_object(self, queryset=None):
        return self.request.user.empresa

# Vista crear empresa (sólo si aún no tiene)
@method_decorator(login_required, name='dispatch')
class EmpresaCreateView(CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'empresa/formulario.html'
    success_url = '/empresa/mi-empresa/'

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'empresa'):
            return redirect('empresa:empresa-detalle')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)
