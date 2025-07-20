from django.shortcuts import render,redirect

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from .models import Usuario,TipoHabitacion,Publicacion,Fotografia,Favorito,ComentarioPublicacion,Calificacion,HistorialEliminacion
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, get_object_or_404
from django.db.models import ProtectedError
import json

# Create your views here.

def login(request):
    return render(request,"login/login.html")


def cerrarSesion(request):
    request.session.flush()
    return redirect('/')

def registro(request):
    return render(request,'login/registrarUsuario.html')






##publicaciones disponibles

def habitaciones(request):
    if 'usuario_id' not in request.session:
        return redirect('/')

    usuario = Usuario.objects.get(id=request.session['usuario_id'])

    publicaciones = Publicacion.objects.filter(estado='ACTIVO').select_related('usuario', 'tipohabitacion')
    tipos=TipoHabitacion.objects.all()

    data = []
    for pub in publicaciones:
        foto = Fotografia.objects.filter(publicacion=pub).order_by('orden').first()
        data.append({
            'id': pub.id,
            'titulo': pub.titulo,
            'precio': pub.precio,
            'descripcion': pub.descripcion,          
            'usuario': pub.usuario.username,
            'foto_url': foto.imagen.url if foto and foto.imagen else None
        })

    return render(request, "habitaciones/index.html", {
        'usuario': usuario,
        'publicaciones': data,
        'tipos':tipos
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

                request.session['usuario_id'] = usuario.id
                request.session['usuario_rol'] = usuario.rol
                request.session['usuario_email'] = usuario.email

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
        first_name = request.POST.get('first_name')  
        last_name = request.POST.get('last_name')    

        if Usuario.objects.filter(email=email).exists():
                messages.error(request, "El correo ya está registrado.")
                return render(request, 'login/registrarUsuario.html')

            # Validar que el nombre de usuario no esté en uso
        if Usuario.objects.filter(username=username).exists():
                messages.error(request, "El nombre de usuario ya existe.")
                return render(request, 'login/registrarUsuario.html')

            # Validar que el teléfono no esté en uso
        if Usuario.objects.filter(telefono=telefono).exists():
                messages.error(request, "El número de teléfono ya está registrado.")
                return render(request, 'login/registrarUsuario.html')

        # Crear usuario
        usuario = Usuario(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            telefono=telefono,
            direccion=direccion,
            password=make_password(password),  
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
    tipos=TipoHabitacion.objects.all()
    return render(request,'administrador/nuevoTipo.html',{'tipos':tipos})

def guardarTipo(request):
    nombre=request.POST['nombre']
    messages.success(request,"Guardado exitosamente")
    tipo=TipoHabitacion.objects.create(nombre=nombre)
    return redirect('/nuevoTipo')
    


def editarTipoHabitacion(request, id):
    tipo = get_object_or_404(TipoHabitacion, id=id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            tipo.nombre = nombre
            tipo.save()
            messages.success(request, "Actualizado correctamente")
            
    return redirect('/nuevoTipo') 


def eliminarTipo(request,id):
    tipo=TipoHabitacion.objects.get(id=id)      
    try:
        tipo.delete()
        messages.success(request, "Tipo de habitación eliminado correctamente.")
    except ProtectedError:
        messages.error(request, "No se puede eliminar porque existen publicaciones relacionadas. Eliminelas y vuelva a intentar.")
    return redirect('/nuevoTipo')

    
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
        
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        usuario.numeroPublicaciones += 1
        usuario.save()

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


def misFavoritos(request):
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    favoritos = Favorito.objects.filter(usuario=usuario).select_related('publicacion')

    

    return render(request, "habitaciones/misFavoritos.html", {
        'usuario': usuario,
        'favoritos': favoritos
    })

def eliminarPublicacion(request,id):
    publi=Publicacion.objects.get(id=id)  
    usuario = publi.usuario 
    fotos = Fotografia.objects.filter(publicacion=publi)
    for foto in fotos:
            if foto.imagen:
                foto.imagen.delete(save=False)
            foto.delete()
    publi.delete()
    if usuario.numeroPublicaciones > 0:
        usuario.numeroPublicaciones -= 1
        usuario.save()
    return redirect('/misPublicaciones')

def eliminarPublicacionAdmin(request,id):
    publi=Publicacion.objects.get(id=id)  
    fotos = Fotografia.objects.filter(publicacion=publi)
    for foto in fotos:
            if foto.imagen:
                foto.imagen.delete(save=False)
            foto.delete()
    publi.delete()
    return redirect('/publicaciones')


def eliminarPublicacionAdmin(request, id):
    motivo = request.POST['motivo']
    publi = Publicacion.objects.get(id=id)

    usuario = None
    if 'usuario_id' in request.session:
        try:
            usuario = Usuario.objects.get(id=request.session['usuario_id'])
        except Usuario.DoesNotExist:
            usuario = None
   
    HistorialEliminacion.objects.create(
    publicacion=publi,
    usuario=usuario,
    motivo=motivo,
    titulo_publicacion=publi.titulo,
    descripcion_publicacion=publi.descripcion,
    )   

    fotos = Fotografia.objects.filter(publicacion=publi)
    for foto in fotos:
        if foto.imagen:
            foto.imagen.delete(save=False)
        foto.delete()

    publi.delete()
    messages.success(request, "Publicación eliminada correctamente con motivo registrado.")
    return redirect('/publicaciones')
   


def eliminarFavorito(request,id):
    fav=Favorito.objects.get(id=id)      
    fav.delete()
    return redirect('/misFavoritos')

   


def detallesPublicacion(request,id):
    publi=Publicacion.objects.get(id=id)  
    
    fotos = Fotografia.objects.filter(publicacion=publi).order_by('orden')

    return render(request, "habitaciones/detallesPublicacion.html", {
        'publicacion': publi,
        'fotos': fotos
    })


def detallesPublicacionAdmin(request,id):
    publi = Publicacion.objects.get(id=id)
    fotos = Fotografia.objects.filter(publicacion=publi).order_by('orden')
    print(f"Fotos encontradas: {fotos.count()}")  # para debug
    return render(request, "administrador/detallesPublicacionAdmin.html", {
        'publicacion': publi,
        'fotos': fotos
    })




##comentario
def publicaciones(request):
    publicaciones = Publicacion.objects.all()

    for pub in publicaciones:
        pub.foto_principal = Fotografia.objects.filter(publicacion=pub).order_by('orden').first()

    return render(request, "administrador/publicaciones.html", {
        'publicaciones': publicaciones  
    })

def usuarios(request):
    usuarios = Usuario.objects.filter(bloqueado=False, rol='Arrendatario')
    return render(request, "administrador/usuariosActivos.html", {'usuarios': usuarios})


def usuariosBloqueados(request):
    usuarios = Usuario.objects.filter(bloqueado=True)
    return render(request, "administrador/usuariosBloqueados.html", {'usuarios': usuarios})


def favoritos(request, id):
    publi = Publicacion.objects.get(id=id)
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    messages.success(request, "Añadido exitosamente")  
    favorito = Favorito.objects.create(usuario=usuario, publicacion=publi)  
    return redirect('/habitaciones')

def guardarComentario(request, id):
    publi = Publicacion.objects.get(id=id)
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    comentario=request.POST.get('comentario')
    messages.success(request, "Añadido exitosamente")  
    comentario = ComentarioPublicacion.objects.create(publicacion=publi,usuario=usuario,texto=comentario)  
    return redirect('/habitaciones')


def calificarPublicacion(request, id):
    publi = Publicacion.objects.get(id=id)
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    puntuacion=request.POST.get('calificacion')
    messages.success(request, "Calificado exitosamente")  
    puntuacion = Calificacion.objects.create(usuario=usuario,publicacion=publi,puntuacion=puntuacion)  
    return redirect('/habitaciones')

# region EDITAR PUBLICACION
def editarPublicacion(request, id):
    publicacion = Publicacion.objects.get(id=id, usuario_id=request.session['usuario_id'])
    tipos = TipoHabitacion.objects.all()
    fotos = Fotografia.objects.filter(publicacion=publicacion).order_by('orden')
        
    return render(request, "habitaciones/editarPublicacion.html", {
        'publicacion': publicacion,
        'tipos': tipos,
        'fotos': fotos
    })

def procesarEdicionPublicacion(request):
    publicacion_id = request.POST.get('publicacion_id')
    titulo = request.POST.get('titulo')
    precio = request.POST.get('precio').replace(',', '.')
    descripcion = request.POST.get('descripcion')
    tipo_id = request.POST.get('tipohabitacion')
    latitud = request.POST.get('latitud').replace(',', '.')
    longitud = request.POST.get('longitud').replace(',', '.')

    nuevas_imagenes = request.FILES.getlist('imagenes[]')

    publicacion = Publicacion.objects.get(
        id=publicacion_id,
        usuario_id=request.session['usuario_id']
    )
    tipo = TipoHabitacion.objects.get(id=tipo_id)

    publicacion.titulo = titulo
    publicacion.precio = precio
    publicacion.descripcion = descripcion
    publicacion.tipohabitacion = tipo
    publicacion.latitud = latitud
    publicacion.longitud = longitud
    publicacion.save()

    if nuevas_imagenes:
        fotos_existentes = Fotografia.objects.filter(publicacion=publicacion)
        for foto in fotos_existentes:
            if foto.imagen:
                foto.imagen.delete(save=False)
            foto.delete()
        
        for index, imagen in enumerate(nuevas_imagenes, start=1):
            Fotografia.objects.create(
                publicacion=publicacion,
                imagen=imagen,
                orden=index
            )

    messages.success(request, "Publicación actualizada correctamente.")
    return redirect('/misPublicaciones')
# endregion

def buscarPublicaciones(request):
    termino = request.GET.get('buscar', '').strip()
    publicaciones_activas = Publicacion.objects.filter(estado='ACTIVO')

    publicaciones_filtradas = publicaciones_activas.filter(
        titulo__icontains=termino
    ) | publicaciones_activas.filter(
        descripcion__icontains=termino
    )

    data = []
    for pub in publicaciones_filtradas:
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

    return render(request, 'habitaciones/index.html', {
        'publicaciones': data,
        'termino_busqueda': termino,
    })


def filtroTipo(request):
    tipo_id = request.GET.get('tipo')
    if tipo_id:
        publicaciones = Publicacion.objects.filter(
            estado='ACTIVO',
            tipohabitacion_id=tipo_id
        ).select_related('usuario', 'tipohabitacion')
    else:
        publicaciones = Publicacion.objects.filter(
            estado='ACTIVO'
        ).select_related('usuario', 'tipohabitacion')

    tipos = TipoHabitacion.objects.all()
    data = []
    for pub in publicaciones:
        foto = Fotografia.objects.filter(publicacion=pub).order_by('orden').first()
        data.append({
            'id': pub.id,
            'titulo': pub.titulo,
            'precio': pub.precio,
            'descripcion': pub.descripcion,
            'tipohabitacion': pub.tipohabitacion.nombre,
            'usuario': pub.usuario.username,
            'foto_url': foto.imagen.url if foto and foto.imagen else None
        })

    return render(request, "habitaciones/index.html", {
        'publicaciones': data,
        'tipos': tipos,
        'tipo_seleccionado': tipo_id
    })

def comentarios(request):
    return render(request,'habitaciones/misComentarios.html')


def misComentarios(request):
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    comentarios = ComentarioPublicacion.objects.filter(usuario=usuario).select_related('publicacion')
    return render(request, "habitaciones/comentarios.html", {
        'usuario': usuario,
        'comentarios': comentarios
    })
    
    
def tipoHabitacion(request):
    return render(request,'habitaciones/tipoHabitacion.html')

def historialPublicaciones(request):
    historial= HistorialEliminacion.objects.all()
    return render(request,'administrador/historialPublicaciones.html',{'historial':historial})


def eliminar_historial(request, id):
    historial = HistorialEliminacion.objects.get(id=id)   
    historial.delete()
    messages.success(request, "Registro de historial eliminado correctamente.")
    return redirect('/historialPublicaciones')



def bloquear_usuario(request, id):
    usuario= Usuario.objects.get(id=id)
    usuario.bloqueado = True
    usuario.save()
    messages.success(request, f'El usuario {usuario.username} ha sido bloqueado.')
    return redirect('/usuarios')  

def desbloquear_usuario(request, id):
    usuario= Usuario.objects.get(id=id)
    usuario.bloqueado = False
    usuario.save()
    messages.success(request, f'El usuario {usuario.username} ha sido desbloqueado.')
    return redirect('/usuariosBloqueados')  


def administrador(request):
    total_usuarios = Usuario.objects.count()
    total_arrendatarios = Usuario.objects.filter(rol='Arrendatario').count()
    total_arrendadores = Usuario.objects.filter(rol='Arrendador').count()
    total_administradores = Usuario.objects.filter(rol='Administrador').count()
    total_publicaciones = Publicacion.objects.count()

    grafico_data = [
        total_usuarios,
        total_arrendatarios,
        total_arrendadores,
        total_administradores,
        total_publicaciones
    ]

    resultados = {
        'total_usuarios': total_usuarios,
        'total_arrendatarios': total_arrendatarios,
        'total_arrendadores': total_arrendadores,
        'total_administradores': total_administradores,
        'total_publicaciones': total_publicaciones,
        'grafico_data_json': json.dumps(grafico_data)
    }

    return render(request, 'administrador/index.html', resultados)