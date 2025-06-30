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
    return render(request,'login/registrarUsuario.html')



def administrador(request):
    if 'usuario_id' not in request.session:
        return redirect('/')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])


    return render(request,"administrador/index.html", {
        'usuario': usuario
    })


##publicaciones disponibles

def habitaciones(request):
    if 'usuario_id' not in request.session:
        return redirect('/')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])

    publicaciones = Publicacion.objects.filter(estado='ACTIVO').select_related('usuario', 'tipohabitacion')

    data = []
    for pub in publicaciones:
        foto = Fotografia.objects.filter(publicacion=pub).order_by('orden').first()
        data.append({
            'id': pub.id,
            'titulo': pub.titulo,
            'precio': pub.precio,
            'descripcion': pub.descripcion,
            'tipo': pub.tipohabitacion.nombre,
            'usuario': pub.usuario.username,
            'foto_url': foto.imagen.url if foto and foto.imagen else None
        })

    return render(request, "habitaciones/index.html", {
        'usuario': usuario,
        'publicaciones': data
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
    

def guardarpublicacion(request):
    if request.method == 'POST':
        titulo = request.POST['titulo']
        precio = request.POST['precio'].replace(',','.')
        descripcion = request.POST['descripcion']
        
        tipo = request.POST['tipohabitacion']
        idtipo=TipoHabitacion.objects.get(id=tipo)
                
        latitud = request.POST.get('latitud')
        longitud = request.POST.get('longitud')
        
        imagenes = request.FILES.getlist('imagenes[]')


        publicacion = Publicacion.objects.create(
            usuario_id=request.session['usuario_id'],
            titulo=titulo,
            precio=precio,
            descripcion=descripcion,
            tipohabitacion=idtipo,
            latitud=latitud,
            longitud=longitud,
           
        )

        for index, imagen in enumerate(imagenes, start=1):
            Fotografia.objects.create(
                publicacion=publicacion,
                imagen=imagen,
                orden=index
            )

        messages.success(request, "Publicación registrada correctamente.")
        return redirect('/habitaciones')

    return redirect('/')




def misPublicaciones(request):
    
    usuario = Usuario.objects.get(id=request.session['usuario_id'])

    publicaciones = Publicacion.objects.filter(usuario=usuario).select_related('tipohabitacion')

    data = []
    for pub in publicaciones:
        foto = Fotografia.objects.filter(publicacion=pub).order_by('orden').first()
        data.append({
            'id': pub.id,
            'titulo': pub.titulo,
            'precio': pub.precio,
            'descripcion': pub.descripcion,
            'tipo': pub.tipohabitacion.nombre,
            'usuario': pub.usuario.username,
            'foto_url': foto.imagen.url if foto and foto.imagen else None
        })

    return render(request, "habitaciones/misPublicaciones.html", {
        'usuario': usuario,
        'publicaciones': data
    })



def eliminarPublicacion(request,id):
    publi=Publicacion.objects.get(id=id)  
    fotos = Fotografia.objects.filter(publicacion=publi)
    for foto in fotos:
            if foto.imagen:
                foto.imagen.delete(save=False)
            foto.delete()
    publi.delete()
    return redirect('/misPublicaciones')
   


def detallesPublicacion(request,id):
    publi=Publicacion.objects.get(id=id)  
    
    fotos = Fotografia.objects.filter(publicacion=publi).order_by('orden')

    return render(request, "habitaciones/detallesPublicacion.html", {
        'publicacion': publi,
        'fotos': fotos
    })

