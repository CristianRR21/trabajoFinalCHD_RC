from django.shortcuts import render,redirect

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from .models import Usuario,TipoHabitacion,Publicacion,Fotografia,Favorito,ComentarioPublicacion,Calificacion,HistorialEliminacion,Mensaje
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, get_object_or_404
from django.db.models import ProtectedError
import json
from django.http import JsonResponse


from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
import mimetypes

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
    publicaciones = Publicacion.objects.filter(estado='ACTIVO').exclude(usuario=usuario).select_related('usuario', 'tipohabitacion')
    tipos=TipoHabitacion.objects.all()

    favoritos_ids = Favorito.objects.filter(usuario=usuario).values_list('publicacion_id', flat=True)
    
    comentarios_pub_ids = ComentarioPublicacion.objects.filter(usuario=usuario).values_list('publicacion_id', flat=True)
    
    calificaciones_pub_ids = Calificacion.objects.filter(usuario=usuario).values_list('publicacion_id', flat=True)
    

    data = []
    for pub in publicaciones:
        foto = Fotografia.objects.filter(publicacion=pub).order_by('orden').first()
        data.append({
            'id': pub.id,
            'titulo': pub.titulo,
            'precio': pub.precio,
            'descripcion': pub.descripcion,
            'usuario': pub.usuario.username,
            'telefono': pub.usuario.telefono,
            'email':pub.usuario.email,
            'tipohabitacion': pub.tipohabitacion.nombre,
            'foto_url': foto.imagen.url if foto and foto.imagen else None
        })

    return render(request, "habitaciones/index.html", {
        'usuario': usuario,
        'publicaciones': data,
        'tipos': tipos,
        'favoritos_ids': set(favoritos_ids),  
        'comentarios_pub_ids': set(comentarios_pub_ids),
        'calificaciones_pub_ids': set(calificaciones_pub_ids),
        # set para búsqueda rápida en el template
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
    
    
 


def comentarios(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login') 

    usuario = Usuario.objects.get(id=usuario_id)
    comentarios = ComentarioPublicacion.objects.filter(usuario=usuario).select_related('publicacion')

    return render(request, "habitaciones/comentarios.html", {
        'usuario': usuario,
        'comentarios': comentarios
    })



def calificaciones(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login') 

    usuario = Usuario.objects.get(id=usuario_id)
    calificaciones = Calificacion.objects.filter(usuario=usuario).select_related('publicacion')

    return render(request, "habitaciones/calificaciones.html", {
        'usuario': usuario,
        'calificaciones': calificaciones
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
    messages.success(request, "Publicación eliminada correctamente.")
    
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
        
    email = EmailMessage(
        subject='Tu publicación ha sido eliminada',
        body=f'Estimado/a {publi.usuario.username},\n\nTu publicación "{publi.titulo}" ha sido eliminada por el administrador.\n\nMotivo: {motivo}\n\nSaludos,\nEquipo de Administración',
        from_email=settings.EMAIL_HOST_USER,
        to=[publi.usuario.email],
    )
    email.send(fail_silently=False)

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
    favorito_existente = Favorito.objects.filter(usuario=usuario, publicacion=publi).first()
    if favorito_existente:
        messages.warning(request, "Esta publicación ya está en tus favoritos.")
    else:
        Favorito.objects.create(usuario=usuario, publicacion=publi)
        messages.success(request, "Añadido exitosamente a favoritos.")

    return redirect('/habitaciones')

def guardarComentario(request, id):
    if request.method == 'POST':
        publi = get_object_or_404(Publicacion, id=id)
        usuario = get_object_or_404(Usuario, id=request.session['usuario_id'])
        texto = request.POST.get('comentario')

        # Evitar duplicados: solo un comentario por usuario por publicación
        existe = ComentarioPublicacion.objects.filter(usuario=usuario, publicacion=publi).exists()
        if not existe:
            ComentarioPublicacion.objects.create(usuario=usuario, publicacion=publi, texto=texto)
            messages.success(request, "Comentario agregado.")
        else:
            messages.warning(request, "Ya tienes un comentario en esta publicación.")

    return redirect('/habitaciones')


def calificarPublicacion(request, id):
    publi = Publicacion.objects.get(id=id)
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    puntuacion=request.POST.get('calificacion')
    existe = Calificacion.objects.filter(usuario=usuario, publicacion=publi).exists()  
        
    if not existe:
            puntuacion = Calificacion.objects.create(usuario=usuario,publicacion=publi,puntuacion=puntuacion)  
            messages.success(request, "Calificado exitosamente")  
    else:
        
            messages.warning(request, "Ya tienes una calificacion en esta publicación.")
       
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

# Mostrar listado de mensajes
def listarMensajes(request):
    mensajes = Mensaje.objects.all()
    return render(request, "listarMensajes.html", {'mensajes': mensajes})
# Mostrar formulario de nuevo mensaje
def nuevoMensaje(request):
    return render(request, "nuevoMensaje.html")
# Guardar nuevo mensaje

def guardarMensaje(request):
    destinatario = request.POST["destinatario"]
    asunto = request.POST["asunto"]
    mensaje_txt = request.POST["mensaje"]
    archivo = request.FILES.get("archivo")
    Mensaje.objects.create(
    destinatario=destinatario,
    asunto=asunto,
    mensaje=mensaje_txt,
    archivo=archivo
    )
    messages.success(request, "Mensaje GUARDADO exitosamente")
    return redirect('/listarMensajes')

# Eliminar mensaje
def eliminarMensaje(request, id):
    mensaje = Mensaje.objects.get(id=id)
# Eliminar archivo adjunto si existe
    if mensaje.archivo and os.path.isfile(mensaje.archivo.path):
        os.remove(mensaje.archivo.path)
    mensaje.delete()
    messages.success(request, "Mensaje ELIMINADO exitosamente")
    return redirect('/listarMensajes')
    # Mostrar formulario de edición
    
def editarMensaje(request, id):
    mensajeEditar = Mensaje.objects.get(id=id)
    return render(request, "editarMensaje.html", {'mensajeEditar': mensajeEditar})
# Procesar edición de mensaje


def procesarEdicionMensaje(request):
    id = request.POST["id"]
    destinatario = request.POST["destinatario"]
    asunto = request.POST["asunto"]
    mensaje_txt = request.POST["mensaje"]
    archivo = request.FILES.get("archivo")
    mensaje = Mensaje.objects.get(id=id)
    mensaje.destinatario = destinatario
    mensaje.asunto = asunto
    mensaje.mensaje = mensaje_txt
    if archivo:
        if mensaje.archivo and os.path.isfile(mensaje.archivo.path):
            os.remove(mensaje.archivo.path)
        mensaje.archivo = archivo
    mensaje.save()
    messages.success(request, "Mensaje ACTUALIZADO exitosamente")
    return redirect('/listarMensajes')

# Enviar mensaje por correo
def enviarMensaje(request, id):
    mensaje = get_object_or_404(Mensaje, id=id)
    email = EmailMessage(
        subject=mensaje.asunto,
        body=mensaje.mensaje,
        from_email=settings.EMAIL_HOST_USER,
        to=[mensaje.destinatario],
    )
    if mensaje.archivo:
        file_type, _ = mimetypes.guess_type(mensaje.archivo.name)
        with open(mensaje.archivo.path, 'rb') as f:
            email.attach(mensaje.archivo.name, f.read(), file_type)
    email.send(fail_silently=False)
    messages.success(request, "Mensaje ENVIADO exitosamente")
    return redirect('/listarMensajes')


def usuariosSistema(request): 
    
    return render(request, "administrador/usuariosSistema.html")



def listadoAdmins(request):
    admins = list(Usuario.objects.filter(rol='Administrador').values())
    return JsonResponse({'admins': admins})

def nuevoAdmin(request):
    user = Usuario.objects.create_user(
        first_name=request.POST.get('first_name'),
        last_name=request.POST.get('last_name'),
        username=request.POST.get('username'),
        email=request.POST.get('email'),
        password=request.POST.get('password'),
        telefono=request.POST.get('telefono'),
        direccion=request.POST.get('direccion'),
        rol='Administrador'
    )
   
    return JsonResponse({'mensaje': 'Administrador creado'})

def editarAdmin(request, id):
    if request.method == 'POST':
        user = Usuario.objects.get(id=id, rol='Administrador')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.username = request.POST.get('username')
        user.telefono = request.POST.get('telefono')
        user.direccion = request.POST.get('direccion')
        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))
        user.save()

        
        return JsonResponse({'mensaje': 'Administrador actualizado'})

def eliminarAdmin(request, id):
    if request.method == 'POST':
        user = Usuario.objects.get(id=id, rol='Administrador')
        user.delete()
        
        
        return JsonResponse({'mensaje': 'Administrador eliminado'})
    
def eliminarComentario(request, id):
    comentario = get_object_or_404(ComentarioPublicacion, id=id)
    comentario.delete()
    return redirect('/comentarios') 