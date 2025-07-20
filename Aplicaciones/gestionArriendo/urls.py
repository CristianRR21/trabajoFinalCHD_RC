from django.urls import path
from.import views
urlpatterns = [
    
    path('',views.login),
   
    path('habitaciones',views.habitaciones),
    path('iniciarSesion',views.iniciarSesion),
    path('cerrarSesion', views.cerrarSesion),
    path('registrarUsuario',views.registrarUsuario),
    path('registro',views.registro),
    
    path('nuevaPublicacion',views.nuevaPublicacion),
    #administrador
    path('administrador',views.administrador),
    path('nuevoTipo',views.nuevoTipo),
    path('guardarTipo',views.guardarTipo),
    
    path('guardarpublicacion',views.guardarpublicacion),
    
    path('misPublicaciones',views.misPublicaciones),
    path('eliminarPublicacion/<id>',views.eliminarPublicacion),
        
    
    path('detallesPublicacion/<id>',views.detallesPublicacion),
    #comentario
    path('publicaciones',views.publicaciones),
    path('usuarios',views.usuarios),
    path('favoritos/<id>',views.favoritos),
    path('editarPublicacion/<id>/', views.editarPublicacion),
    path('procesarEdicionPublicacion/', views.procesarEdicionPublicacion),
    path('guardarComentario/<id>/',views.guardarComentario),
    path('calificarPublicacion/<id>/',views.calificarPublicacion),
    path('misFavoritos',views.misFavoritos),
    path('eliminarFavorito/<id>',views.eliminarFavorito),
    path('buscar/', views.buscarPublicaciones),
    path('filtroTipo/', views.filtroTipo, name='filtro_tipo'),

    path('comentarios',views.comentarios),
    path('tipohabitacion',views.tipoHabitacion),
    path('editarTipoHabitacion/<int:id>/',views.editarTipoHabitacion),
    path('eliminarTipo/<id>',views.eliminarTipo),
    
    path('eliminarPublicacionAdmin/<id>/',views.eliminarPublicacionAdmin),
    

  path('detallesPublicacionAdmin/<id>',views.detallesPublicacionAdmin),
  path('historialPublicaciones',views.historialPublicaciones),
    
  
 path('eliminar_historial/<int:id>/', views.eliminar_historial),
 
 path('bloquear_usuario/<int:id>/', views.bloquear_usuario),
  path('desbloquear_usuario/<int:id>/', views.desbloquear_usuario),
 

    path('usuariosBloqueados',views.usuariosBloqueados),






    

    
    
]
