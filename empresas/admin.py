# empresa/admin.py
from django.contrib import admin
from .models import Empresa
from django.utils.html import format_html

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_establecimiento',
        'usuario',
        'telefono',
        'correo',
        'slug',
        'logo_preview',
    )
    readonly_fields = ['slug', 'creado', 'actualizado', 'logo_preview']
    search_fields = ['nombre_establecimiento', 'usuario__username']
    list_filter = ['creado']
    prepopulated_fields = {'slug': ('nombre_establecimiento',)}

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 80px;" />', obj.logo.url)
        return "Sin logo"
    logo_preview.short_description = 'Logo'

    fieldsets = (
        ('Datos Básicos', {
            'fields': ('usuario', 'nombre_establecimiento', 'telefono', 'correo', 'direccion', 'slug')
        }),
        ('Logo', {
            'fields': ('logo', 'logo_preview')
        }),
        ('Tiempos', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )
