from django.db import models
from productos.models import Producto

class Carrito(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'

class Pedido(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    detalles = models.TextField(blank=True, null=True)
    correo = models.EmailField()
    necesita_factura = models.BooleanField(default=False)
    numero_documento = models.CharField(max_length=50, blank=True, null=True)
    archivo_rut = models.FileField(upload_to='facturas/', blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido de {self.nombre} - {self.correo}"
