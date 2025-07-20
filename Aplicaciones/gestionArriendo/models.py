from django.db import models
from django.contrib.auth.models import AbstractUser


#from django.contrib.auth.models import AbstractUser
# Create your models here. 
    
     
class Usuario(AbstractUser):
    telefono = models.CharField(max_length=10)
    direccion = models.TextField()
    rol = models.TextField(default='Arrendatario')
    bloqueado = models.BooleanField(default=False)
    def __str__(self):
        return self.username   
         
    
    

class TipoHabitacion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.TextField()


class Publicacion(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    titulo = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    tipohabitacion = models.ForeignKey(TipoHabitacion, on_delete=models.PROTECT)
    latitud = models.DecimalField(max_digits=20, decimal_places=9)
    longitud = models.DecimalField(max_digits=20, decimal_places=9)
    fechacreacion = models.DateField(auto_now_add=True)
    estado = models.TextField(default='ACTIVO') 




class Fotografia(models.Model):
    id = models.AutoField(primary_key=True)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='publicaciones', null=True, blank=True)
    orden = models.IntegerField()


    
    
    
    
class HistorialEliminacion(models.Model):
    id = models.AutoField(primary_key=True)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.SET_NULL, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    motivo = models.TextField()
    fechaeliminacion = models.DateField(auto_now_add=True)
    titulo_publicacion = models.CharField(max_length=255, null=True, blank=True)
    descripcion_publicacion = models.TextField(null=True, blank=True)


class BloqueoUsuario(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha_bloqueo = models.DateField(auto_now_add=True)

class Favorito(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    fechaagregado = models.DateField(auto_now_add=True)

class Calificacion(models.Model):
    id = models.AutoField(primary_key=True)
    usuario= models.ForeignKey(Usuario, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    puntuacion = models.IntegerField()
    fecha = models.DateField(auto_now_add=True)

class HistorialVisualizacion(models.Model):
    id = models.AutoField(primary_key=True)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    usuario= models.ForeignKey(Usuario, on_delete=models.CASCADE)
    

class ComentarioPublicacion(models.Model):
    id = models.AutoField(primary_key=True)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateField(auto_now_add=True)
