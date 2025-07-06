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
 
    
    
    
    
    
]
