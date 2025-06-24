from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la categoría")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icono = models.CharField(max_length=50, null=True, blank=True, verbose_name="Ícono de FontAwesome")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    DISPONIBILIDAD_CHOICES = [
        (True, 'Disponible'),
        (False, 'No disponible'),
    ]

    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Costo unitario del producto")
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio actual de venta")
    imagen = ProcessedImageField(
        upload_to='productos/',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 80},
        null=True,
        blank=True,
        verbose_name="Imagen principal"
    )
    disponible = models.BooleanField(default=True, choices=DISPONIBILIDAD_CHOICES)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    caracteristicas = models.TextField(blank=True)
    punto_reorden = models.PositiveIntegerField(default=5, help_text="Cantidad mínima antes de reordenar")
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('productos:producto-detail', args=[str(self.id)])

    @property
    def stock(self):
        entradas = self.movimientos.filter(tipo='entrada').aggregate(models.Sum('cantidad'))['cantidad__sum'] or 0
        salidas = self.movimientos.filter(tipo='salida').aggregate(models.Sum('cantidad'))['cantidad__sum'] or 0
        return entradas - salidas


class ProductoImage(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = ProcessedImageField(
        upload_to='productos/',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 80},
        null=True,
        blank=True
    )
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']
        verbose_name = "Imagen de producto"
        verbose_name_plural = "Imágenes de productos"

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"
