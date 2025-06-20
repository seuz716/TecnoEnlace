from django.shortcuts import render

def contacto(request):
    return render(request, 'contacto.html')

def politica_privacidad(request):
    return render(request, 'politica_privacidad.html')

def terminos_servicio(request):
    return render(request, 'terminos_servicio.html')


def custom_404(request, exception):
    return render(request, "404.html", status=404)

def custom_500(request):
    return render(request, "500.html", status=500)