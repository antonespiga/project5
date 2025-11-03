from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import os
from django.contrib.auth import authenticate, login, logout
from .forms import ActivityForm, LoginForm, RegisterForm
from .models import Activity, User
from .tcx_parse_calc import parse_calc_tcx
from .fill_data import fill_data
from datetime import date
from datetime import datetime, timedelta
from .utils import crear_img
from math import pow, floor

# Create your views here.
def dashboard(request):
    activities = Activity.objects.filter(usuario = request.user).order_by('-fecha')
    total_activities = len(activities)
    total_distance = 0
    total_seconds = 0
    totales = []
    
    for activity in activities:
        seconds = string_to_seconds(activity.acums["acum_tiempo"])
        total_distance += float(activity.acums["acum_distancia"])
        total_seconds += seconds
    total_time = seconds_to_string(total_seconds)
    totales = {"total_activities": total_activities, "total_distance": round(total_distance, 2), "total_time": total_time}
    semana, total_semana = crear_calendario(activities)
    
    return render(request, 'mapas/dashboard.html', {
        "activities": activities,
        "calendario": semana,
        "total_semana": total_semana,
        "totales": totales
    })

def index(request):
    return render(request, "mapas/index.html")

def activities(request):
    if request.method == 'POST':
        activities = Activity.objects.get(usuario=request.user)
        return render(request, "mapas/activities.html", {
            "activities": activities
        })
    elif request.method == 'GET':
        activities = Activity.objects.filter(usuario = request.user);
        return render(request, "mapas/activities.html", {
            "activities": activities,
        })

def handle_data(activity):
    file = activity.archivo_tcx
    data = parse_calc_tcx(file)
    puntos = data["puntos"]
    for punto in puntos:
        activity.bpm.append(punto["heart_rate"]) if punto["heart_rate"]  else None
        activity.coordenadas.append(punto["coordenadas"]) if punto["coordenadas"] is not None else [0,0]
        activity.altitudes.append(punto["altitud"])
        activity.distancias.append(punto["distancia"])
        activity.tiempos.append(punto["time"])
        activity.cadencias.append(punto["cadencia"])
    activity.lap_data = data["lap_data"]
    activity.acums = data["acums"]
    activity.fecha = data["fecha"]
    activity.sport = data["sport"]
    activity.imagen = f"img_{activity.id}.png"
    activity.puntos = puntos
   
    activity.save()
    crear_img(activity.coordenadas, activity.id)
    return activity


def activity_view(request, activity_id):
    activity = Activity.objects.get(pk=activity_id)
    return render(request, "mapas/activity_view.html", {
        "activity": activity,
    })

def delete_activity(request, activity_id):
    activity = Activity.objects.get(pk=activity_id)
    activity.delete()
    return HttpResponseRedirect(reverse("index"))

def add_activity(request):
    if(request.method == 'POST'):
        archivo = request.FILES.get('archivo_tcx')
        
        form = ActivityForm(request.POST, request.FILES)
        if form.is_valid():
            activity =  Activity()
            activity.usuario = request.user
            activity.nombre = form["nombre"].value()
            activity.descripcion = form["descripcion"].value()
            activity.archivo_tcx = archivo
            activity.url_archivo = form["url_archivo"].value()
           
            activity.save()
            activity_parsed = handle_data(activity)
            return render(request, "mapas/activity_view.html", {
                "activity": activity_parsed,
            })
            
    else:
        form = ActivityForm()
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
                return HttpResponseRedirect(reverse("dashboard"))
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
    print("user logged out")
    logout(request)
    print("user logged out")
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

def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    return render(request, "mapas/profile.html", {
        "user": user
    })

def crear_calendario(activities):
    today = date.today()
    inicio = today -  timedelta(days = 7 + today.weekday())
    fin = inicio + timedelta(days=6)
    nom = ["L", "M", "X", "J", "V", "S", "D"]
    semana =  []
    totales = []
    actividades = []

    for activity in activities:
        if((activity.fecha.date()) >= inicio and activity.fecha.date() <= fin):
            actividades.append(activity)
    distancia_run = 0; distancia_swimm = 0; distancia_other = 0;
    tiempo_run = 0; tiempo_swimm = 0; tiempo_other = 0;
    subida_run = 0; subida_swimm = 0; subida_other =0;
    cont_run = 0; cont_swimm = 0; cont_other = 0;

    for i in range(7):
        a = None
        for actividad in actividades:
            if(actividad.fecha.day == (inicio + timedelta(days=i)).day):
                if((actividad.sport.lower()) == "running"):
                    cont_run += 1;
                    distancia_run += float(actividad.acums["acum_distancia"])
                    tiempo_run += float(string_to_seconds(actividad.acums["acum_tiempo"]))
                    subida_run += float(actividad.acums["acum_subida"])
                elif((actividad.sport.lower() == "swimming")):
                    cont_swimm += 1;
                    distancia_swimm += float(actividad.acums["acum_distancia"])
                    tiempo_swimm += float(string_to_seconds(actividad.acums["acum_tiempo"]))
                    subida_swimm += float(actividad.acums["acum_subida"])
                elif((actividad.sport.lower() == "other")):
                    cont_other += 1;
                    distancia_run += float(actividad.acums["acum_distancia"])
                    tiempo_other += float(string_to_seconds(actividad.acums["acum_tiempo"]))
                    subida_other += float(actividad.acums["acum_subida"])
                
                    
                a = {
                    "id": actividad.id,
                    "sport": actividad.sport,
                    "link": (str(actividad.sport)).lower()+".svg" if actividad is not None else None,
                    "acums": actividad.acums
                }   
            
        semana.append( {
            "dia": nom[i],
            "fecha": (inicio + timedelta(days=i)).day,
            "actividad": a,
            "is_today": ((inicio + timedelta(days=i)) == date.today())
        } )
    tiempo_str_run = seconds_to_string(tiempo_run)
    tiempo_str_swimm = seconds_to_string(tiempo_swimm)
    tiempo_str_other = seconds_to_string(tiempo_other)

    totales = {"running":{"activities_run": cont_run,"distancia": round(distancia_run, 2), "tiempo": tiempo_str_run, "subida": floor(subida_run)},
               "swimming": {"acitities_swimm": cont_swimm,"distancia": round(distancia_swimm, 2), "tiempo": tiempo_str_swimm, "subida": floor(subida_swimm)},
               "other": {"activities_other": cont_other, "distancia": round(distancia_other, 2), "tiempo": tiempo_str_other, "subida": floor(subida_other)}}
    return(semana, totales)

def string_to_seconds(time):
    todo = time.split(":")
    l = len(todo)
    seconds = 0
    for i in range(l ):
        seconds += (int(pow(60, int(l-i-1))) * float(todo[i]))
    return seconds     

def seconds_to_string(seconds):
    int_seconds = int(seconds)
    h = floor(int_seconds / 3600)
    m = floor( (int_seconds % 3600) / 60)
    s = (int_seconds) % 60
    return(f"{h:2}h{m:02}m{s:02}s")