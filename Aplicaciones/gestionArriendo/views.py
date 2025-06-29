from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from .models import Usuario
# Create your views here.
def administrador(request):
    return render(request,"administrador/index.html")


def login(request):
    return render(request,"login/login.html")

def habitaciones(request):
    return render(request,"habitaciones/index.html")

#def iniciarSesion(request):


def iniciarSesion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(email=email)

            if check_password(password, usuario.password):
                if usuario.bloqueado:
                    messages.error(request, "Usuario bloqueado.")
                    return redirect('/')

                # Guardar sesión
                request.session['usuario_id'] = usuario.id
                request.session['usuario_rol'] = usuario.rol
                request.session['usuario_email'] = usuario.email

                # Redirección según rol
                if usuario.rol == 'Administrador':
                    return redirect('/administrador')
                elif usuario.rol in ['Arrendador', 'Arrendatario']:
                    return redirect('/habitaciones')
                else:
                    messages.error(request, "Rol desconocido.")
                    return redirect('/')
            else:
                messages.error(request, "Contraseña incorrecta.")
                return redirect('/')
        except Usuario.DoesNotExist:
            messages.error(request, "Correo no registrado.")
            return redirect('/')

    return render(request, 'login/login.html')


def cerrarSesion(request):
    request.session.flush()
    return redirect('/')
