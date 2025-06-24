import os
from dotenv import load_dotenv
import google.generativeai as genai
from productos.models import Producto
from django.conf import settings

# Cargar variables de entorno
load_dotenv()

# Configurar la clave de API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Diccionario básico para manejar sesiones de chat por usuario
chat_sessions = {}

def obtener_chat_session(usuario_id):
    """Devuelve una sesión de chat para un usuario (inicia una nueva si no existe)"""
    if usuario_id not in chat_sessions:
        model = genai.GenerativeModel("gemini-1.5-flash")
        chat_sessions[usuario_id] = model.start_chat(history=[])
    return chat_sessions[usuario_id]

def generar_contexto_de_productos(filtro=None):
    """Genera una descripción de los productos disponibles (opcionalmente filtrados)"""
    productos = Producto.objects.filter(disponible=True)

    if filtro:
        productos = productos.filter(nombre__icontains=filtro)

    contexto = ""
    for p in productos:
        contexto += (
            f"- {p.nombre} (${p.precio})\n"
            f"  {p.descripcion}\n"
            f"  Características: {p.caracteristicas}\n"
            f"  Categoría: {p.categoria.nombre}\n"
            f"  Stock: {p.stock}\n\n"
        )
    return contexto or "No hay productos disponibles en este momento."

def preguntar_a_gemini(pregunta_usuario, usuario_id="anonimo"):
    """Envía una pregunta al modelo Gemini usando contexto del catálogo"""
    try:
        contexto = generar_contexto_de_productos()

        prompt = (
            "Eres un **Asistente de Ventas Experto** y amigable de nuestra tienda. Tu misión principal es **proporcionar información precisa y útil sobre nuestros productos disponibles**, y **motivar sutilmente al usuario a realizar una compra**, destacando el valor y los beneficios.\n\n"
            "**Directrices Clave:**\n"
            "1. **Claridad y Concisión:** Responde de forma directa y fácil de entender. Evita rodeos innecesarios.\n"
            "2. **Enfoque en el Valor:** Al describir un producto, resalta siempre **qué problema resuelve o qué beneficio clave** ofrece al cliente. No solo listes características, explícales por qué son importantes.\n"
            "3. **Incentivo a la Acción (Suave):** Después de proporcionar la información, incluye una frase amable que invite a la compra, como '¡No te quedes sin el tuyo!', '¡Aprovecha esta oportunidad!', o 'Haz clic para comprar ahora y transformar tu día/espacio/rutina.' Adapta el mensaje al producto.\n"
            "4. **Recomendaciones Inteligentes:** Si la pregunta es abierta o busca algo general (ej. '¿Qué me recomiendas?'), sugiere productos que sabes que son populares o que se ajusten a una necesidad común, y por qué.\n"
            "5. **Manejo de Desvíos:** Si la pregunta no está directamente relacionada con nuestros productos o el inventario, responde de forma educada y profesional, redirigiendo al usuario a que consulte el catálogo o realice preguntas sobre este. Por ejemplo: 'Mi función es ayudarte con información sobre nuestro catálogo de productos. ¿Hay algo específico que te gustaría saber sobre ellos?'\n"
            "6. **Formato de Respuesta:** Presenta la información de manera limpia, idealmente con el nombre del producto destacado y luego sus detalles relevantes.\n\n"
            "--- **Catálogo de Productos Actual (Información Esencial)** ---\n"
            f"{contexto}\n"
            "--- **Pregunta del Cliente** ---\n"
            f"{pregunta_usuario}\n\n"
            "**Tu Respuesta Detallada y Persuasiva:**"
        )

        chat = obtener_chat_session(usuario_id)

        # ✨ Aquí se aplica la configuración de generación
        response = chat.send_message(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=200,     # Puedes ajustar este valor según lo que necesites
                temperature=0.7,
                top_p=0.95,
                top_k=60
            )
        )

        return response.text

    except Exception as e:
        return f"⚠️ Error al generar respuesta: {str(e)}"
