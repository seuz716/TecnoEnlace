from django.db import models
from django.utils import timezone
from productos.models import Producto

class MovimientoInventario(models.Model):
    TIPO_CHOICES = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    # Fecha automática del sistema
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro (sistema)")

    # ✅ Fecha editable de transacción
    fecha_transaccion = models.DateField(
        verbose_name="Fecha de la transacción",
        default=timezone.now
    )

    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.tipo.capitalize()} - {self.producto.nombre} ({self.cantidad})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.actualizar_producto()

    def actualizar_producto(self):
        producto = self.producto
        entradas = MovimientoInventario.objects.filter(producto=producto, tipo='entrada')
        salidas = MovimientoInventario.objects.filter(producto=producto, tipo='salida')

        total_entradas = sum(e.cantidad for e in entradas)
        total_salidas = sum(s.cantidad for s in salidas)

        total_costo = sum(e.cantidad * e.costo_unitario for e in entradas)
        precio_promedio = total_costo / total_entradas if total_entradas else 0

        producto.precio = precio_promedio
        producto.save()
