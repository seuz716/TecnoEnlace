from django.contrib import admin
from .models import Categoria, Producto, ProductoImage

# --------------------------
# Admin de Categorías
# --------------------------
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'icono')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}
    ordering = ('nombre',)
    list_per_page = 20


# --------------------------
# Inline para Imágenes de Productos
# --------------------------
class ProductoImageInline(admin.TabularInline):
    model = ProductoImage
    extra = 3
    fields = ('imagen', 'orden',)
    ordering = ('orden',)


# --------------------------
# Admin de Productos
# --------------------------
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'precio',
        'costo',
        'stock_display',
        'disponible',
        'categoria',
        'creado',
    )
    list_editable = (
        'precio',
        'costo',
        'disponible',
    )
    search_fields = ('nombre', 'categoria__nombre')
    list_filter = ('disponible', 'categoria')
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('creado', 'actualizado', 'stock_display')
    ordering = ('-creado',)
    list_per_page = 20
    inlines = [ProductoImageInline]

    fieldsets = (
        ('📦 Información del Producto', {
            'fields': (
                'nombre',
                'slug',
                'descripcion',
                'categoria',
                'imagen',
            )
        }),
        ('💲 Precio y Costo', {
            'fields': (
                'precio',
                'costo',
                'disponible',
            )
        }),
        ('📦 Stock Calculado', {
            'fields': ('stock_display',),
        }),
        ('🧾 Características Adicionales', {
            'fields': ('caracteristicas',),
            'classes': ('collapse',),
        }),
        ('📅 Fechas de Registro', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',),
        }),
    )

    def stock_display(self, obj):
        return obj.stock
    stock_display.short_description = 'Stock Actual'
