
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("rutas", views.rutas, name="rutas"),
    path("rutas/agregar", views.add_ruta, name="add_ruta"),
    path("rutas/delete/<int:ruta_id>", views.delete_ruta, name="delete_ruta"),
    path("rutas/<int:ruta_id>", views.ruta_view, name="ruta_view")
]
