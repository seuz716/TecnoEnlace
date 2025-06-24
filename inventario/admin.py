from django.contrib import admin
from .models import MovimientoInventario

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = (
        'producto',
        'tipo',
        'cantidad',
        'costo_unitario',
        'fecha_transaccion',
        'fecha'
    )
    list_filter = ('tipo', 'fecha_transaccion', 'producto')
    search_fields = ('producto__nombre',)
    readonly_fields = ('fecha',)
