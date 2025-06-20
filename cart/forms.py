from django import forms
from .models import Carrito
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?56\s?9\s?\d{4}\s?\d{4}$',
    message="Formato válido: +56 9 1234 5678"
)

class PedidoForm(forms.ModelForm):
    nombre = forms.CharField(
        label="Nombre Completo",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control-lg animated-input',
            'placeholder': 'Ej: Juan Pérez',
            'autocomplete': 'name'
        }),
        help_text="Ingrese su nombre completo"
    )

    telefono = forms.CharField(
        label="Teléfono",
        max_length=20,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control-lg animated-input',
            'placeholder': 'Ej: +56 9 1234 5678',
            'autocomplete': 'tel',
            'data-mask': '+56 9 9999 9999'
        }),
        help_text="Debe incluir el código de país y el número (Ej: +56 9 1234 5678)"
    )

    direccion = forms.CharField(
        label="Dirección de Entrega",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control-lg animated-input',
            'rows': 1,
            'placeholder': 'Ej: Av. Principal #123, Depto 45',
            'autocomplete': 'street-address',
            'data-geocomplete': 'true'
        }),
        help_text="Incluya referencias como esquinas o edificios conocidos"
    )

    class Meta:
        model = Carrito
        fields = ['nombre', 'telefono', 'direccion']
