#gemini_reportes.py
import os
from decimal import Decimal
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Carga segura de API KEY
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("❌ API de Gemini no encontrada. Define 'GEMINI_API_KEY' en tu .env.")

# 2. Configura Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Función para formatear movimientos de forma compacta
def formatear_movimientos_tabla(movimientos):
    tabla = "Fecha | Tipo | Cantidad | Costo/U | Total | Saldo\n"
    tabla += "-" * 55 + "\n"
    for m in movimientos:
        tabla += f"{m['fecha']} | {m['tipo']} | {m['cantidad']} | ${m['costo_unitario']} | ${m['costo_total']} | {m['saldo']}\n"
    return tabla

# 4. Generador de análisis de Kardex
def generar_kardex_analisis(producto_nombre, movimientos):
    resumen = formatear_movimientos_tabla(movimientos)
    prompt = f"""
📊 Análisis Kardex - Producto: {producto_nombre}

{resumen}

🎯 Como auditor experto en inventarios y revisión fiscal, realiza un análisis del comportamiento del producto. Responde brevemente:
- ¿Hay patrones de sobreinventario o rotación lenta?
- ¿El precio promedio y saldo son adecuados?
- ¿Qué acciones debe tomar el administrador para mejorar eficiencia y control de inventarios?
    """.strip()

    try:
        respuesta = model.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"❌ Error con Gemini: {str(e)}"

# 5. Generador de análisis de valoración de inventario
def generar_analisis_valoracion(productos, total_valor):
    resumen = "Producto | Stock | Costo/U | Valor Total\n"
    resumen += "-" * 45 + "\n"
    for p in productos:
        resumen += f"{p['nombre']} | {p['stock']} | ${p['costo_unitario']} | ${p['valor_total']}\n"

    prompt = f"""
📦 Informe de Valoración de Inventario Actual

{resumen}
🧾 Valor total del inventario: ${total_valor:,.2f}

🔍 Eres un experto colombiano en auditoría financiera, revisión fiscal y gestión de inventario. Analiza:
- ¿Qué riesgos contables o fiscales se detectan?
- ¿Dónde puede estar el capital inmovilizado innecesariamente?
- ¿Qué medidas debe implementar el administrador para mejorar la eficiencia y rotación del inventario?
- ¿Recomendarías método promedio, FIFO o LIFO en este caso?

Da respuestas claras y prácticas para la gerencia.
    """.strip()

    try:
        respuesta = model.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"❌ Error generando análisis: {str(e)}"


def generar_analisis_rentabilidad(productos):
    resumen = "Producto | Costo Promedio | Precio Venta | Margen % | Rentabilidad\n"
    resumen += "-" * 60 + "\n"
    for p in productos:
        resumen += (
            f"{p['nombre']} | ${p['costo_promedio']} | ${p['precio']} | "
            f"{p['margen_porcentaje']}% | {p['clasificacion']}\n"
        )

    prompt = f"""
📊 Informe de Rentabilidad por Producto

{resumen}

📌 Como experto en auditoría, finanzas y control de precios, analiza:
- ¿Qué productos presentan márgenes bajos?
- ¿Hay precios mal establecidos o productos no rentables?
- ¿Qué acciones recomienda para mejorar la rentabilidad y eficiencia comercial?
Responde con claridad para un administrador de PyME en Colombia.
    """

    try:
        respuesta = model.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"❌ Error en análisis Gemini: {str(e)}"

def generar_analisis_cmv(movimientos, total_cmv):
    prompt = "📦 Análisis de Costo de Mercancía Vendida (CMV)\n\n"
    for m in movimientos[:10]:  # Para no gastar tokens, mostramos solo los primeros 10
        prompt += f"- {m['fecha']} | {m['producto']} | {m['cantidad']} x ${m['costo_unitario']} = ${m['costo_total']}\n"
    prompt += f"\n🧾 Total CMV: ${total_cmv:,.2f}\n\n"
    prompt += "Como experto contable y auditor, analiza este CMV y su impacto en la utilidad bruta. Sugiere acciones si el costo parece elevado respecto a ventas."

    try:
        respuesta = model.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"❌ Error generando análisis CMV: {str(e)}"


def generar_analisis_cmv(data, producto_nombre=None):
    prompt = f"""
    Analiza los siguientes datos mensuales de Costo de Mercancía Vendida (CMV), ingresos y utilidad bruta:
    Producto: {producto_nombre or 'Todos'}
    Datos:
    {data}
    
    Proporciona un análisis claro de tendencias, meses más rentables y menos rentables. 
    No expliques los datos fila por fila. Sé sintético pero informativo.
    """

    try:
        respuesta = model.generate_content(prompt)
        return respuesta.text.strip()
    except Exception as e:
        return f"[Error al generar análisis IA: {str(e)}]"


def generar_analisis_inventario(data):
    prompt = f"""
    Analiza la siguiente lista de productos con sus respectivos stocks, costos y precios:

    {data}

    Comenta sobre el estado del inventario: qué productos tienen stock bajo, cuáles representan mayor inversión, si hay exceso de inventario, etc.
    Hazlo claro, útil y sin repetir los datos tal como están.
    """

    try:
        respuesta = model.generate_content(prompt)
        return respuesta.text.strip()
    except Exception as e:
        return f"[Error al generar análisis IA: {str(e)}]"


def generar_analisis_reorden(productos_bajos):
    prompt = f"""
    Los siguientes productos están por debajo de su punto de reorden:
    
    {productos_bajos}

    Analiza cuáles podrían causar desabastecimiento, cuáles son más críticos y sugiere acciones.
    """
    try:
        respuesta = model.generate_content(prompt)
        return respuesta.text.strip()
    except Exception as e:
        return f"[Error al generar análisis IA: {str(e)}]"

def generar_analisis_historial(nombre_producto, movimientos):
    prompt = f"""
    A continuación, se presenta el historial de movimientos del producto "{nombre_producto}".

    Cada movimiento incluye: fecha, tipo (entrada o salida), cantidad, costo unitario y observaciones.

    Datos:
    {movimientos}

    Por favor, genera un análisis que incluya patrones de entradas y salidas, posibles alertas de salidas anormales o irregularidades, y recomendaciones de mejora en la gestión del inventario de este producto.
    """
    try:
        respuesta = model.generate_content(prompt)
        return respuesta.text.strip()
    except Exception as e:
        return f"[Error al generar análisis IA: {str(e)}]"
