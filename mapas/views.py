from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import os
from django.contrib.auth import authenticate, login, logout
from .forms import RutaForm, LoginForm, RegisterForm
from .models import Ruta, User
from .tcx_parse_calc import parse_calc_tcx
from .fill_data import fill_data

# Create your views here.
def index(request):
    rutas = Ruta.objects.all()
    return render(request, 'mapas/index.html', {
        "rutas": rutas
    })

def rutas(request):
    if request.method == 'POST':
        rutas = Ruta.objects.all()
        return render(request, "mapas/rutas.html", {
            "rutas": rutas
        })
    elif request.method == 'GET':
        rutas = Ruta.objects.filter(usuario = request.user);
        return render(request, "mapas/rutas.html", {
            "rutas": rutas,
        })

def handle_ruta(ruta):
    file = ruta.archivo_tcx
    data = parse_calc_tcx(file)
    filled = fill_data(data)
    
    speeds = data["speeds"]
    puntos = data["puntos"]
    ruta.bpm = filled["hrs"]
    ruta.sport = data["sport"]
    ruta.coordenadas = filled["coordenadas"]
    ruta.altitudes = filled["altitudes"]
    ruta.distancias = filled["distancias"]
    ruta.tiempos = filled["times"]
    ruta.cadencias = filled["cadencias"]
    ruta.lap_data = data["lap_data"]
    ruta.acums = data["acums"]
    ruta.fecha = data["fecha"]
    ruta.save()
    return ruta, speeds, puntos

def ruta_view(request, ruta_id):
    ruta = Ruta.objects.get(pk=ruta_id)
    ruta_parsed,  speeds, puntos = handle_ruta(ruta)

    return render(request, "mapas/ruta_view.html", {
        "ruta": ruta_parsed,
        "speeds": speeds,
        "puntos": puntos
    })

def delete_ruta(request, ruta_id):
    
    ruta = Ruta.objects.get(pk=ruta_id)
    ruta.delete()
    return HttpResponseRedirect(reverse("index"))

def add_ruta(request):
    if(request.method == 'POST'):
        archivo = request.FILES.get('archivo_tcx')
        
        form = RutaForm(request.POST, request.FILES)
        if form.is_valid():
            ruta =  Ruta()
            ruta.usuario = request.user
            ruta.nombre = form["nombre"].value()
            ruta.descripcion = form["descripcion"].value()
            ruta.archivo_tcx = archivo
            ruta.url_archivo = form["url_archivo"].value()
            ruta.save()
            ruta_parsed, speeds, puntos = handle_ruta(ruta)

            return render(request, "mapas/ruta_view.html", {
                "ruta": ruta_parsed,
                "speeds": speeds,
                "puntos": puntos
            })
            
    else:
        form = RutaForm()
    return render(request, "mapas/agregar.html", {
    "form": form
    })

def login_view(request):
    if(request.method == "POST"):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                print("user logged")
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "mapas/login.html", {
                    "form": form,
                    "error": "Datos incorrectos"
                })
        else:
            return render(request, "mapas/login.html", {
                "form": form,
                "error": "Formulario no valido"
            })
        
    else:
        form = LoginForm()
    return render(request, "mapas/login.html", {
        "form": form
    })

def logout_view(request):
    print("user logget out")
    logout(request)
    print("user logget out")
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if(request.method == "POST"):
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            
            user = User.objects.create(
                username = username,
                password = password,
                email = email
            )
            user.set_password(password)
            user.save()
            print(user)
            return render(request, "mapas/index.html")
        else:
            return render(request, "mapas/register.html", {
                "form": form
            })
        
    else:
        form = RegisterForm()
        return render(request, "mapas/register.html", {
            "form": form
        })