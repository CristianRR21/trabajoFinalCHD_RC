from django.urls import path
from.import views
urlpatterns = [
    
    path('',views.login),
    path('administrador',views.administrador),
    path('habitaciones',views.habitaciones),
    path('iniciarSesion',views.iniciarSesion),
    path('cerrarSesion', views.cerrarSesion),
    
]
