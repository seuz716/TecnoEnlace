from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Empresa(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empresa')
    nombre_establecimiento = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    direccion = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    logo = models.ImageField(
        upload_to='logos_empresas/',
        blank=True,
        null=True,
        help_text="Sube el logo de la empresa (idealmente en formato PNG o SVG)."
    )

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre_establecimiento']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre_establecimiento)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_establecimiento
