from django.shortcuts import render,redirect

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from .models import Usuario,TipoHabitacion,Publicacion,Fotografia
from django.contrib.auth.hashers import make_password

# Create your views here.

def login(request):
    return render(request,"login/login.html")


def cerrarSesion(request):
    request.session.flush()
    return redirect('/')

def registro(request):
    return render(request,'login/registrarUsuario')



def administrador(request):
    if 'usuario_id' not in request.session:
        return redirect('/')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])


    return render(request,"administrador/index.html", {
        'usuario': usuario
    })



def habitaciones(request):
    if 'usuario_id' not in request.session:
        return redirect('/')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])

    return render(request, "habitaciones/index.html", {
        'usuario': usuario
    })



def iniciarSesion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(email=email)

            if check_password(password, usuario.password):
                if usuario.bloqueado:
                    messages.error(request, "Usuario bloqueado.")
                    return render(request, 'login/login.html')

                # Guardar sesión AQUI ES DONDE YA MANEJO EL REGISTRO DE DATOS PARA LA SESSION
                request.session['usuario_id'] = usuario.id
                request.session['usuario_rol'] = usuario.rol
                request.session['usuario_email'] = usuario.email

                # Mostrar directamente la plantilla correspondiente
                if usuario.rol == 'Administrador':
                    return redirect('/administrador')
                elif usuario.rol in ['Arrendador', 'Arrendatario']:
                    return redirect('/habitaciones')
                else:
                    messages.error(request, "Rol desconocido.")
                    return render(request, 'login/login.html')
            else:
                messages.error(request, "Contraseña incorrecta.")
                return render(request, 'login/login.html')

        except Usuario.DoesNotExist:
            messages.error(request, "Correo no registrado.")
            return render(request, 'login/login.html')

    return render(request, 'login/login.html')






def registrarUsuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        first_name = request.POST.get('first_name')  # para nombres
        last_name = request.POST.get('last_name')    # para apellidos

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'login/registrarUsuario.html')

        # Crear usuario
        usuario = Usuario(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            telefono=telefono,
            direccion=direccion,
            password=make_password(password),  # encriptar contraseña
        )
        usuario.save()
        messages.success(request, "Usuario registrado correctamente.")
        return redirect('/')

    return render(request, 'login/registrarUsuario.html')

def nuevaPublicacion(request):
    tipos=TipoHabitacion.objects.all()
    return render(request,'habitaciones/nuevaPublicacion.html',{'tipos':tipos})

#administrador
def nuevoTipo(request):
    return render(request,'administrador/nuevoTipo.html')

def guardarTipo(request):
    nombre=request.POST['nombre']
    messages.success(request,"Guardado exitosamente")
    tipo=TipoHabitacion.objects.create(nombre=nombre)
    return render(request,"administrador/index.html")
    

def guardarPublicacion(request):
    if request.method == 'POST':
        titulo = request.POST['titulo']
        precio = request.POST['precio']
        descripcion = request.POST['descripcion']
        tipo_id = request.POST['tipohabitacion']
        latitud = request.POST['latitud']
        longitud = request.POST['longitud']
        imagenes = request.FILES.getlist('imagenes[]')

        if len(imagenes) > 5:
            messages.error(request, "No puedes subir más de 5 imágenes.")
            return redirect('/nuevaPublicacion')  # o como se llame tu URL

        publicacion = Publicacion.objects.create(
            titulo=titulo,
            precio=precio,
            descripcion=descripcion,
            tipo_id=tipo_id,
            latitud=latitud,
            longitud=longitud,
            usuario_id=request.session['usuario']  # si usas sesión
        )

        for imagen in imagenes:
            Fotografia.objects.create(
                publicacion=publicacion,imagen=imagen
            )

        messages.success(request, "Publicación registrada correctamente.")
        return redirect('/habitaciones')

    return redirect('/')