from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .gemini_api import preguntar_a_gemini

@require_POST
def chat_ia(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        pregunta = request.POST.get("pregunta")
        if pregunta:
            usuario_id = (
                str(request.user.id) if request.user.is_authenticated
                else request.session.session_key or "anonimo"
            )
            respuesta = preguntar_a_gemini(pregunta, usuario_id)
            return JsonResponse({'respuesta': respuesta})
        return JsonResponse({'error': 'No se recibió la pregunta'}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)
