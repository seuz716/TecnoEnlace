from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la categoría")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icono = models.CharField(max_length=50, null=True, blank=True, verbose_name="Ícono de FontAwesome")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    DISPONIBILIDAD_CHOICES = [
        (True, 'Disponible'),
        (False, 'No disponible'),
    ]

    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    # Puedes eliminar o mantener este campo si deseas una imagen principal
    imagen = ProcessedImageField(
        upload_to='productos/',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 80},
        null=True,
        blank=True
    )
    stock = models.IntegerField(default=0)
    disponible = models.BooleanField(default=True, choices=DISPONIBILIDAD_CHOICES)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    caracteristicas = models.TextField()
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

# Modelo para múltiples imágenes por producto
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
    # Opcional: un campo para ordenar las imágenes
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"
