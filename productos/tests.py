from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Categoria, Producto

class CategoriaViewTests(TestCase):
    
    def setUp(self):
        # Crear y loguear un usuario
        self.user = get_user_model().objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

        # Datos de categoría inicial
        self.categoria_data = {
            'nombre': 'Categoría Test',
            'slug': 'categoria-test'
        }
        self.categoria = Categoria.objects.create(**self.categoria_data)

    def test_categoria_list_view(self):
        url = reverse('productos:categoria-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.categoria.nombre)
        self.assertTemplateUsed(response, 'productos/categoria_list.html')

    def test_categoria_create_view(self):
        url = reverse('productos:categoria-create')
        data = {'nombre': 'Nueva Categoría', 'slug': 'nueva-categoria'}
        response = self.client.post(url, data)
        # Ahora, como estamos logueados, debería redirigir a la lista
        self.assertRedirects(response, reverse('productos:categoria-list'))
        self.assertTrue(Categoria.objects.filter(slug='nueva-categoria').exists())

    def test_categoria_update_view(self):
        url = reverse('productos:categoria-update', args=[self.categoria.pk])
        data = {'nombre': 'Categoría Actualizada', 'slug': 'categoria-actualizada'}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('productos:categoria-list'))
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nombre, 'Categoría Actualizada')

    def test_categoria_delete_view(self):
        url = reverse('productos:categoria-delete', args=[self.categoria.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('productos:categoria-list'))
        self.assertFalse(Categoria.objects.filter(pk=self.categoria.pk).exists())

    def test_categoria_delete_view_not_logged_in(self):
        # Cerrar sesión para probar la redirección al login
        self.client.logout()
        url = reverse('productos:categoria-delete', args=[self.categoria.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}')



class ProductoViewTests(TestCase):
    def setUp(self):
        # Crear y loguear un usuario para las vistas protegidas
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        # Crear categoría y producto base
        self.categoria = Categoria.objects.create(nombre='CatTest', slug='cattest')
        self.producto = Producto.objects.create(
            nombre='ProdTest',
            slug='prodtest',
            descripcion='Descripción de prueba',
            precio=50.00,
            categoria=self.categoria,
            disponible=True
        )

def test_producto_list_view(self):
        url = reverse('productos:producto-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.producto.nombre)
        self.assertTemplateUsed(response, 'productos/producto_list.html')

def test_producto_create_view(self):
    url = reverse('productos:producto-create')
    data = {
        'nombre': 'NuevoProd',
        'slug': 'nuevoprod',
        'descripcion': 'Desc nueva',
        'precio': 75.00,
        'categoria': self.categoria.pk,
        'disponible': True
    }
    response = self.client.post(url, data)
    self.assertRedirects(response, reverse('productos:producto-list'))
    self.assertTrue(Producto.objects.filter(slug='nuevoprod').exists())

def test_producto_update_view(self):
        url = reverse('productos:producto-update', args=[self.producto.pk])
        data = {
            'nombre': 'ProdEditado',
            'slug': 'proded',
            'descripcion': 'Desc editada',
            'precio': 60.00,
            'categoria': self.categoria.pk,
            'disponible': True
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('productos:producto-list'))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'ProdEditado')

def test_producto_delete_view(self):
    url = reverse('productos:producto-delete', args=[self.producto.pk])
    response = self.client.post(url)
    self.assertRedirects(response, reverse('productos:producto-list'))
    self.assertFalse(Producto.objects.filter(pk=self.producto.pk).exists())


def test_producto_detail_view(self):
    # Vista pública, no hace falta login
    self.client.logout()
    url = reverse('productos:producto-detail', args=[self.producto.pk])
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.producto.nombre)
    self.assertTemplateUsed(response, 'productos/producto_detail.html')

def test_producto_client_list_view(self):
    # Crear un producto no disponible para probar el filtro
    Producto.objects.create(
        nombre='NoDisp',
        slug='nodisp',
        descripcion='No visible',
        precio=20.00,
        categoria=self.categoria,
        disponible=False
    )
    url = reverse('productos:producto_client_list')
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.producto.nombre)
    self.assertNotContains(response, 'NoDisp')
    self.assertTemplateUsed(response, 'productos/producto_client_list.html')

def test_list_filter_by_category(self):
        otra = Categoria.objects.create(nombre='Otra', slug='otra')
        prod2 = Producto.objects.create(
            nombre='EnOtra',
            slug='enotra',
            descripcion='Desc',
            precio=30.00,
            categoria=otra,
            disponible=True
        )
        url = reverse('productos:producto-list') + f'?categoria={otra.slug}'
        response = self.client.get(url)
        self.assertContains(response, prod2.nombre)
        self.assertNotContains(response, self.producto.nombre)

def test_list_order_by_price_asc(self):
    barato = Producto.objects.create(
        nombre='Barato',
        slug='barato',
        descripcion='Desc',
        precio=10.00,
        categoria=self.categoria,
        disponible=True
    )
    url = reverse('productos:producto-list') + '?priceFilter=asc'
    response = self.client.get(url)
    content = response.content.decode()
    # Asegura que «Barato» aparece antes que «ProdTest»
    self.assertTrue(content.index('Barato') < content.index('ProdTest'))

def test_list_order_by_price_desc(self):
    caro = Producto.objects.create(
        nombre='Caro',
        slug='caro',
        descripcion='Desc',
        precio=100.00,
        categoria=self.categoria,
        disponible=True
    )
    url = reverse('productos:producto-list') + '?priceFilter=desc'
    response = self.client.get(url)
    content = response.content.decode()
    # Asegura que «Caro» aparece antes que «ProdTest»
    self.assertTrue(content.index('Caro') < content.index('ProdTest'))
