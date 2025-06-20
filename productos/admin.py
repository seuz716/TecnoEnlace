from django.contrib import admin
from .models import Categoria, Producto, ProductoImage

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'icono')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}
    ordering = ('nombre',)
    list_per_page = 20

class ProductoImageInline(admin.TabularInline):
    model = ProductoImage
    extra = 6  # Se mostrarán 6 formularios en blanco para nuevas imágenes
    fields = ('imagen', 'orden',)
    ordering = ('orden',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'disponible', 'categoria', 'creado')
    search_fields = ('nombre', 'categoria__nombre')
    list_filter = ('disponible', 'categoria')
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('creado', 'actualizado')
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'slug', 'descripcion', 'categoria', 'imagen')
        }),
        ('Precio y disponibilidad', {
            'fields': ('precio', 'stock', 'disponible')
        }),
        ('Datos avanzados', {
            'fields': ('caracteristicas',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-creado',)
    list_editable = ('precio', 'stock', 'disponible')
    list_per_page = 20
    inlines = [ProductoImageInline]
