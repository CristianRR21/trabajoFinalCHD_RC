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

def registro(request):
    return render(request,'login/registro.html')


def registrarUsuario(request):
    if request.method == 'POST':
        first_name = request.POST.get('nombres')
        last_name = request.POST.get('apellidos')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        password = request.POST.get('password')
        confirmar_password = request.POST.get('confirmar_password')

        # Verificar contraseñas
        if password != confirmar_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('/registro')

        # Verificar si ya existe el correo
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'El correo ya está registrado.')
            return redirect('/registro')

        # Crear usuario
        usuario = Usuario(
            username=email,  
            first_name=first_name,
            last_name=last_name,
            email=email,
            telefono=telefono,
            direccion=direccion,
            rol='Arrendatario'  # por defecto
        )
        usuario.set_password(password)
        usuario.save()

        messages.success(request, 'Registro exitoso. Inicia sesión.')
        return redirect('/')

    return render(request, 'login/registro.html') 