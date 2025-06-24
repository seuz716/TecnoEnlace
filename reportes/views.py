# views.py
from collections import defaultdict

from decimal import Decimal, InvalidOperation
# Django
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.db.models import DecimalField


# Modelos
from productos.models import Producto
from inventario.models import MovimientoInventario




# Funciones de análisis (Gemini)
from reportes.gemini_reportes import (
    generar_kardex_analisis,
    generar_analisis_valoracion,
    generar_analisis_rentabilidad,
    generar_analisis_cmv,generar_analisis_historial  # 👈 asegúrate de tener esta función

)


class HistorialProductoView(TemplateView):
    template_name = 'reportes/historial_producto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto_id = self.kwargs.get('producto_id')
        producto = get_object_or_404(Producto, id=producto_id)
        movimientos = producto.movimientos.order_by('-fecha_transaccion', '-id')

        # 🧠 IA: preparar los datos para el análisis
        movimientos_data = [{
            'fecha': str(m.fecha_transaccion),
            'tipo': m.get_tipo_display(),
            'cantidad': m.cantidad,
            'costo_unitario': float(m.costo_unitario),
            'observaciones': m.observaciones
        } for m in movimientos]

        analisis_ia = generar_analisis_historial(producto.nombre, movimientos_data)

        context.update({
            'producto': producto,
            'movimientos': movimientos,
            'analisis_ia': analisis_ia,
        })
        return context


class ProductosBajoStockView(TemplateView):
    template_name = 'reportes/productos_bajo_stock.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productos_bajos = Producto.objects.all()
        bajos = [
            {
                'nombre': p.nombre,
                'stock': p.stock,
                'punto_reorden': p.punto_reorden,
                'categoria': p.categoria.nombre,
                'precio': p.precio
            }
            for p in productos_bajos if p.stock < p.punto_reorden
        ]

        from reportes.gemini_reportes import generar_analisis_reorden
        analisis = generar_analisis_reorden(bajos)

        context['productos_bajos'] = bajos
        context['analisis_ia'] = analisis
        return context



class InventarioActualView(TemplateView):
    template_name = 'reportes/inventario_actual.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productos = Producto.objects.all()

        inventario = []
        for p in productos:
            inventario.append({
                'nombre': p.nombre,
                'categoria': p.categoria.nombre,
                'stock': p.stock,
                'costo': p.costo,
                'precio': p.precio,
                'valor_total': round(p.stock * (p.costo or 0), 2)
            })

        # 👇 Análisis IA con Gemini
        from reportes.gemini_reportes import generar_analisis_inventario
        analisis = generar_analisis_inventario(inventario)

        context['inventario'] = inventario
        context['analisis_ia'] = analisis
        return context


class CMVMensualView(TemplateView):
    template_name = 'reportes/cmv_mensual.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto_id = self.request.GET.get('producto')
        producto_filtrado = Producto.objects.filter(id=producto_id).first() if producto_id else None

        movimientos = MovimientoInventario.objects.all()
        if producto_filtrado:
            movimientos = movimientos.filter(producto=producto_filtrado)

        movimientos = movimientos.annotate(
            periodo=F('fecha_transaccion__month'),
            anio=F('fecha_transaccion__year'),
            total=ExpressionWrapper(F('cantidad') * F('costo_unitario'), output_field=DecimalField())
        )

        data = defaultdict(lambda: {'entradas': Decimal('0.00'), 'salidas': Decimal('0.00')})
        for m in movimientos:
            clave = f"{m.anio}-{str(m.periodo).zfill(2)}"
            if m.tipo == 'entrada':
                data[clave]['entradas'] += m.total
            elif m.tipo == 'salida':
                data[clave]['salidas'] += m.total

        reporte_ordenado = [
            {
                'periodo': k,
                'compras': v['entradas'],
                'ventas': v['salidas'],
                'cmv': v['entradas'],
                'ingresos': v['salidas'],
                'utilidad_bruta': v['salidas'] - v['entradas']
            }
            for k, v in sorted(data.items())
        ]
        # 👇 Llamada a Gemini
        analisis_ia = generar_analisis_cmv(reporte_ordenado, producto_filtrado.nombre if producto_filtrado else None)

        context['analisis_ia'] = analisis_ia


        context['productos'] = Producto.objects.all()
        context['producto_seleccionado'] = producto_filtrado
        context['reporte'] = reporte_ordenado
        return context



class CMVView(TemplateView):
    template_name = 'reportes/cmv.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        salidas = MovimientoInventario.objects.filter(tipo='salida')

        # Sumar (cantidad * costo_unitario) para cada salida
        total_cmv = salidas.aggregate(
            cmv=Sum(
                ExpressionWrapper(
                    F('cantidad') * F('costo_unitario'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )['cmv'] or Decimal('0.00')

        movimientos = salidas.order_by('-fecha_transaccion')
        detalles = [{
            'producto': m.producto.nombre,
            'fecha': m.fecha_transaccion,
            'cantidad': m.cantidad,
            'costo_unitario': m.costo_unitario,
            'costo_total': m.costo_unitario * m.cantidad
        } for m in movimientos]

        # Análisis IA con Gemini
        analisis = generar_analisis_cmv(detalles, total_cmv)

        context.update({
            'total_cmv': total_cmv,
            'salidas': detalles,
            'analisis': analisis,
        })
        return context


class KardexProductoView(TemplateView):
    template_name = 'reportes/kardex.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto = get_object_or_404(Producto, id=self.kwargs['producto_id'])
        movimientos_qs = MovimientoInventario.objects.filter(producto=producto).order_by('fecha_transaccion', 'id')

        saldo = 0
        data = []

        for mov in movimientos_qs:
            saldo += mov.cantidad if mov.tipo == 'entrada' else -mov.cantidad
            data.append({
                'fecha': mov.fecha_transaccion.strftime('%Y-%m-%d'),
                'tipo': mov.get_tipo_display(),
                'cantidad': mov.cantidad,
                'costo_unitario': mov.costo_unitario,
                'costo_total': mov.costo_unitario * mov.cantidad,
                'saldo': saldo,
            })

        # 👇 Análisis automático con Gemini
        analisis_ia = generar_kardex_analisis(producto.nombre, data)

        context.update({
            'producto': producto,
            'movimientos': data,
            'analisis_ia': analisis_ia,
        })
        return context


class ValoracionInventarioView(TemplateView):
    template_name = 'reportes/valoracion_inventario.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productos = Producto.objects.all()

        total_valor_inventario = 0
        productos_data = []

        for producto in productos:
            stock = producto.stock
            costo_unitario = producto.costo or 0  # usa tu campo de costo
            valor_total = stock * costo_unitario
            total_valor_inventario += valor_total

            productos_data.append({
                'nombre': producto.nombre,
                'stock': stock,
                'costo_unitario': float(costo_unitario),
                'valor_total': float(valor_total),
            })

        # Análisis IA con Gemini
        analisis_ia = generar_analisis_valoracion(productos_data, float(total_valor_inventario))

        context['productos'] = productos_data
        context['total_valor_inventario'] = total_valor_inventario
        context['analisis_ia'] = analisis_ia
        return context



class RentabilidadProductosView(TemplateView):
    template_name = 'reportes/rentabilidad.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productos = Producto.objects.all()
        resultado = []

        for prod in productos:
            entradas = prod.movimientos.filter(tipo='entrada')
            total_entradas = entradas.aggregate(total=Sum('cantidad'))['total'] or 0

            # Costo total como Decimal
            total_costo = entradas.aggregate(
                costo=Sum(
                    ExpressionWrapper(
                        F('cantidad') * F('costo_unitario'),
                        output_field=DecimalField(max_digits=12, decimal_places=2)
                    )
                )
            )['costo'] or Decimal('0.00')

            try:
                costo_promedio = (total_costo / Decimal(total_entradas)).quantize(Decimal('0.01')) if total_entradas else Decimal('0.00')
                margen = (prod.precio - costo_promedio).quantize(Decimal('0.01'))
                margen_pct = ((margen / costo_promedio) * 100).quantize(Decimal('0.01')) if costo_promedio else Decimal('0.00')
            except (InvalidOperation, ZeroDivisionError):
                costo_promedio = margen = margen_pct = Decimal('0.00')

            resultado.append({
                'nombre': prod.nombre,
                'precio': prod.precio,
                'costo_promedio': costo_promedio,
                'margen': margen,
                'margen_porcentaje': margen_pct,
                'clasificacion': 'Alta' if margen_pct > 30 else 'Media' if margen_pct > 15 else 'Baja',
            })

        context['productos'] = resultado
        context['analisis'] = generar_analisis_rentabilidad(resultado)
        return context
