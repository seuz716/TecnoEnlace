from django import forms
from .models import Categoria, Producto

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'slug', 'icono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'icono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-solid fa-box'}),
        }

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'slug', 'descripcion', 'precio', 'imagen', 'stock', 'disponible', 'categoria', 'caracteristicas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'caracteristicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        