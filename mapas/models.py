from django.db import models
from django.contrib.auth.models import AbstractUser




# Create your models here.
class User(AbstractUser):
    edad = models.IntegerField(default=None, blank=True, null=True)
    altura = models.FloatField(max_length=20, default=None, blank=True, null=True)
    peso = models.FloatField(max_length=20, default=None, blank=True, null=True)
    fc_reposo = models.FloatField(max_length=20, default=None, blank=True, null=True)
    fc_max = models.FloatField(max_length=20, default=None, blank=True, null=True)
    card_z1 = models.FloatField(max_length=20, default=None, blank=True, null=True)
    card_z2 = models.FloatField(max_length=20, default=None, blank=True, null=True)
    card_z3 = models.FloatField(max_length=20, default=None, blank=True, null=True)
    card_z4 = models.FloatField(max_length=20, default=None, blank=True, null=True)
    
    pass

class Activity(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ruta_user", default=None)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    ubicacion = models.JSONField(default=list, blank=True, null=True)
    fecha = models.DateTimeField(default=None, blank=True, null=True)
    sport = models.CharField(max_length=200, default=None, blank=True, null=True)
    tiempo = models.FloatField(max_length=20, default=None, blank=True, null=True)
    distancia = models.FloatField(max_length=20, default=None, blank=True, null=True)
    subida = models.FloatField(max_length=20, default=None, blank=True, null=True)
    fc_med = models.FloatField(max_length=20, default=None, blank=True, null=True)
    ritmo = models.CharField(max_length=20, default=None, blank=True, null=True)
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