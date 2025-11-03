from django.db import models
from django.contrib.auth.models import AbstractUser




# Create your models here.
class User(AbstractUser):
    pass

class Activity(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ruta_user", default=None)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha = models.DateTimeField(default=None, blank=True, null=True)
    sport = models.CharField(max_length=200, default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    url_archivo = models.CharField(max_length=200, blank=True)
    archivo_gpx = models.FileField(upload_to='rutas/', default=None)
    archivo_tcx = models.FileField(upload_to='rutas/', default=None)
    coordenadas = models.JSONField(default=list)
    altitudes = models.JSONField(default=list)
    distancias = models.JSONField(default=list)
    tiempos = models.JSONField(default=list)
    cadencias = models.JSONField(default=list)
    bpm = models.JSONField(default=list)
    lap_data = models.JSONField(default=list)
    acums = models.JSONField(default=list)
    imagen = models.CharField(max_length=200, default=None, blank=True, null=True)
    puntos = models.JSONField(default=list)

    def __str__(self):
        return self.nombre