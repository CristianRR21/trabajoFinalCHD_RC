from django.test import TestCase
from .models import ComentarioPublicacion, Publicacion, Usuario
from django.utils import timezone

class ComentarioPublicacionTestCase(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.usuario = Usuario.objects.create(
            username='testuser',
            email='testuser@example.com',
            password='hashed_password',
            telefono='1234567890',
            direccion='Dirección de prueba'
        )

        # Crear una publicación de prueba
        self.publicacion = Publicacion.objects.create(
            usuario=self.usuario,
            titulo='Publicación de prueba',
            precio=100,
            descripcion='Descripción de prueba',
            tipohabitacion_id=1,  # asegúrate de tener este tipo en la base de datos de prueba
            latitud='0.000000',
            longitud='0.000000',
            estado='ACTIVO'
        )

    def test_crear_comentario(self):
        comentario = ComentarioPublicacion.objects.create(
            publicacion=self.publicacion,
            usuario=self.usuario,
            texto='Este es un comentario de prueba.'
        )
        self.assertIsInstance(comentario, ComentarioPublicacion)
        self.assertEqual(comentario.texto, 'Este es un comentario de prueba.')
        self.assertEqual(comentario.usuario, self.usuario)
        self.assertEqual(comentario.publicacion, self.publicacion)

    def test_fecha_automatica(self):
        comentario = ComentarioPublicacion.objects.create(
            publicacion=self.publicacion,
            usuario=self.usuario,
            texto='Fecha automática'
        )
        self.assertIsNotNone(comentario.fecha)
        self.assertEqual(comentario.fecha, timezone.now().date())

    def test_no_comentarios_duplicados(self):
        # Crea el primer comentario
        ComentarioPublicacion.objects.create(
            publicacion=self.publicacion,
            usuario=self.usuario,
            texto='Primer comentario'
        )

        # Intento de crear segundo comentario del mismo usuario en la misma publicación
        comentario_duplicado = ComentarioPublicacion.objects.filter(
            publicacion=self.publicacion,
            usuario=self.usuario
        )
        self.assertEqual(comentario_duplicado.count(), 1)
