from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from mapas.tcx_parse_calc import getUbicacion
from .forms import ActivityForm, LoginForm, RegisterForm, Delete_confirmForm
from .models import Activity, User

from .fill_data import fill_data
from datetime import date
from datetime import datetime, timedelta
from .utils import crear_img, normalize_data
from .utils import handle_data, string_to_seconds, seconds_to_string
from math import pow, floor
import logging
import calendar
import requests

logger = logging.getLogger(__name__)

# Create your views here.
def dashboard(request):
    activities = Activity.objects.filter(usuario = request.user).order_by('-fecha')
    total_activities = activities.count()
    total_activities_run = 0; total_activities_swimm = 0; total_activities_other = 0;
    total_distance_run = 0; total_distance_swimm = 0; total_distance_other = 0;
    total_seconds_run = 0; total_seconds_swimm = 0; total_seconds_other = 0;
    total_activities_year = 0;
    total_activities_run_year = 0; total_activities_swimm_year = 0; total_activities_other_year = 0;
    total_distance_run_year = 0; total_distance_swimm_year = 0; total_distance_other_year = 0;
    total_seconds_run_year = 0; total_seconds_swimm_year = 0; total_seconds_other_year = 0;
    totales = []
    
    for activity in activities:
        try:
            acums = normalize_data(activity.acums)
            sport = activity.sport.lower() or ""
            if(sport == 'running'):
                total_activities_run += 1
                seconds_run = string_to_seconds(acums.get("acum_tiempo"))
                total_distance_run += float(acums.get("acum_distancia"))
                total_seconds_run += seconds_run
                if(activity.fecha).year == 2025:
                    total_activities_run_year += 1;
                    seconds_run_year = string_to_seconds(acums.get("acum_tiempo"))
                    total_distance_run_year += float(acums.get("acum_distancia"))
                    total_seconds_run_year += seconds_run_year
            elif(sport == 'swimming'):
                total_activities_swimm += 1
                seconds_swimm = string_to_seconds(acums.get("acum_tiempo"))
                total_distance_swimm += float(acums.get("acum_distancia"))
                total_seconds_swimm += seconds_swimm
                if(activity.fecha).year == 2025:
                    total_activities_swimm_year += 1;
                    seconds_swimm_year = string_to_seconds(acums.get("acum_tiempo"))
                    total_distance_swimm_year += float(acums.get("acum_distancia"))
                    total_seconds_swimm_year += seconds_swimm_year
            elif (sport == 'other'):
                total_activities_other += 1
                seconds_other = string_to_seconds(acums.get("acum_tiempo"))
                total_distance_other += float(acums.get("acum_distancia"))
                total_seconds_other += seconds_other
                if(activity.fecha).year == 2025:
                    total_activities_other_year += 1;
                    seconds_other_year = string_to_seconds(acums.get("acum_tiempo"))
                    total_distance_other_year += float(acums.get("acum_distancia"))
                    total_seconds_other_year += seconds_other_year
        except Exception as e:
            logger.exception("Error en id=%s: %s", getattr(activity, 'id', None), e)
    total_activities_year = total_activities_run_year + total_activities_swimm_year + total_activities_other_year
    total_time_run = seconds_to_string(total_seconds_run); total_time_run_year = seconds_to_string(total_seconds_run_year)
    total_time_swimm = seconds_to_string(total_seconds_swimm); total_time_swimm_year = seconds_to_string(total_seconds_swimm_year);
    total_time_other = seconds_to_string(total_seconds_other); total_time_other_year = seconds_to_string(total_seconds_other_year);
    total_time = seconds_to_string(float(total_seconds_run + total_seconds_swimm + total_seconds_other))
    total_time_year = seconds_to_string(float(total_seconds_run_year + total_seconds_swimm_year + total_seconds_other_year))
    total_distance = float(total_distance_run + total_distance_swimm + total_distance_other)
    total_distance_year = float(total_distance_run_year + total_distance_swimm_year + total_distance_other_year)
    
    totales = {"total_activities": total_activities, "total_time": total_time, "total_distance": round(total_distance, 2), 
               "total_activities_year": total_activities_year, "total_time_year": total_time_year, "total_distance_year": round(total_distance_year, 2),
               "total_activities_run": total_activities_run, "total_distance_run": round(total_distance_run, 2), "total_time_run": total_time_run,
               "total_activities_swimm": total_activities_swimm, "total_distance_swimm": round(total_distance_swimm, 2), "total_time_swimm": total_time_swimm,
               "total_activities_other": total_activities_other, "total_distance_other": round(total_distance_other, 2), "total_time_other": total_time_other,
               "total_activities_run_year": total_activities_run_year, "total_distance_run_year": round(total_distance_run_year, 2), "total_time_run_year": total_time_run_year,
               "total_activities_swimm_year": total_activities_swimm_year, "total_distance_swimm_year": round(total_distance_swimm_year, 2), "total_time_swimm_year": total_time_swimm_year,
               "total_activities_other_year": total_activities_other_year, "total_distance_other_year": round(total_distance_other_year, 2), "total_time_other_year": total_time_other_year,}
    diario, semana, total_semana = crear_semana(activities)
   
    return render(request, 'mapas/dashboard.html', {
        "activities": activities,
        "calendario": diario,
        "semana": semana,
        "total_semana": total_semana,
        "totales": totales
    })

def index(request):
    if(request.user.is_authenticated):
        return render(request, "mapas/index.html")
    else:
        return render(request, "mapas/login.html")

def activities(request):
    if request.method == 'POST':
        activities = Activity.objects.get(usuario=request.user)
        return render(request, "mapas/activities.html", {
            "activities": activities
        })
    elif request.method == 'GET':
        
        activities = Activity.objects.filter(usuario = request.user).order_by("-fecha");
        return render(request, "mapas/activities.html", {
            "activities": activities,
            "state": 'asc'
        })

def actualizar(request):
    activities = Activity.objects.filter(usuario=request.user)
    for activity in activities:
        if activity.ritmo == None:
            ritmo = activity.acums.get("avg_speed")
            setattr(activity, 'ritmo', ritmo)
            activity.save()


def activities_sorted(request, campo, state):
    if campo == 'ubicacion':
        campo = 'ubicacion__city'
    if state == 'asc':
        ordering = f"{campo}"
        state="desc"
    else:
        ordering = f"-{campo}"
        state = 'asc'
    activities_sorted = Activity.objects.filter(usuario=request.user).order_by(ordering)
    return render(request, "mapas/activities.html", {
        "activities": activities_sorted, 
        "state": state
    })

def activities_semana(request, year=None, semana=None):
    dia_semana_texto = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    hoy = timezone.now()
    dia_semana = hoy.weekday()
    lunes_actual = hoy - timedelta(days = dia_semana)
    diario = [] 
    datos_semana = [] 
    if year == None:
        year_numero = hoy.isocalendar().year
    else:
        year_numero = year
    
    if semana == None:
        lunes = lunes_actual
        semana_numero = lunes.date().isocalendar().week
    else:
        semana_numero = semana
       
    lunes = (date.fromisocalendar(year_numero, semana_numero, 1 )) 
    domingo = lunes + timedelta(days = 6)
    
    actividades_semana = Activity.objects.filter(fecha__gte=lunes, fecha__lt=domingo + timedelta(days = 1), usuario=request.user).order_by("-fecha")
    
    for i in range(7):
        dia = lunes + timedelta(days = i)
        acts_dia = actividades_semana.filter(fecha__date=dia) if actividades_semana.exists() else actividades_semana.filter(fecha=dia)
       
        acum_dist = 0
        # serializar los datos del dia y append a la semana
        for act_dia in acts_dia:
            acum_dist += float(act_dia.acums["acum_distancia"])
        datos_semana.append({
        "dia": dia.isoformat(),
        "dia_semana": dia.weekday(),
        "distancia": acum_dist
        })
    
    prev_lunes = (lunes - timedelta(days = 7)).isocalendar()
    next_lunes = (lunes + timedelta(days = 7)).isocalendar()
    
    prev_week = prev_lunes.week;
    prev_year = prev_lunes.year
    next_week = next_lunes.week;
    next_year = next_lunes.year
    
    return render(request, "mapas/activities_semana.html", {
        "activities": actividades_semana,
        "datos_semana": datos_semana,
        "year_actual": year_numero,
        "semana_actual": semana_numero,
        "lunes": lunes,
        "domingo": domingo,
        "prev_week":prev_week,
        "prev_year": prev_year,
        "next_week": next_week ,
        "next_year": next_year
    })

def activities_mes(request, year=None, mes=None):
    hoy = timezone.now()
    mes_selec = mes if mes is not None else hoy.date().month
    year_selec = year if year is not None else hoy.isocalendar().year
    
    if(mes_selec == 12):
        next_month = 1
        next_year = int(year_selec) + 1
    else:
        next_month = mes_selec + 1
        next_year = year_selec
    
    if(mes_selec == 1):
        prev_month = 12
        prev_year= int(year_selec) - 1
    else:
        prev_month = mes_selec - 1
        prev_year = int(year_selec)
    
    activities_mes = Activity.objects.filter(fecha__month=mes_selec, fecha__year=year_selec, usuario=request.user).order_by("-fecha")
    weeks = crear_mes(mes_selec, year_selec, request.user)
    activities_mes_dias = crear_dias_mes(mes_selec, year_selec, request.user)
    return render(request, "mapas/activities_mes.html", {
        "activities_mes": activities_mes_dias,
        "mes_actual" : mes_selec,
        "year_actual" : year_selec,
        "next_month": next_month,
        "next_year": next_year,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "weeks": weeks
    })

def activities_year(request, year=None):
    hoy = timezone.now()
    year_sel = year if year is not None else hoy.date().year
    activities_year = Activity.objects.filter(fecha__year=year_sel, usuario=request.user).order_by("fecha")
    year_by_mes, year_tots = crear_year(year_sel, request.user)
    return render(request, 'mapas/activities_year.html', {
        "activities": activities_year,
        "count": activities_year.count(),
        "year": year_sel,
        "prev_year": int(year_sel) - 1,
        "next_year": int(year_sel) + 1,
        "year_by_mes": year_by_mes,
        "year_tots": year_tots
    })

def activity_view(request, activity_id):
    activity = Activity.objects.get(pk=activity_id)
    
    return render(request, "mapas/activity_view.html", {
        "activity": activity,
       
    })
    #key=pk.7ac696b7ea0768eddd3c991d72540a63


def delete_activity(request, activity_id):
    activity = Activity.objects.get(pk=activity_id)
    if(request.method == 'POST'):
        try:
            activity.delete()
            messages.success(request, "Actividad eliminada")
        except Exception as e:
            logger.exception("Error al eliminar activity %s: %s",activity_id, e)
            messages.error(request, "Error al eliminar actividad")
    
        return redirect("activities")
    else:
        return render(request, "mapas/delete_activity.html", {
            "activity": activity
        })
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

def profile_fisico(request, user_id):
    user = User.objects.get(pk=user_id)
    return render(request, "mapas/profile_fisico.html", {
        "user": user
    })

def crear_semana(activities):
    today = date.today()
    inicio = today -  timedelta(days = today.weekday())
    fin = inicio + timedelta(days=6)
    nom = ["L", "M", "X", "J", "V", "S", "D"]
    diario = []
    semana =  []
    semana_sport = []
    d_semana = []
    semana_run = []
    semana_swimm = []
    semana_other = []
    totales = []
    actividades = []

    actividades = [a for a in activities if getattr(a, "fecha", None) and inicio <= a.fecha.date() <= fin]
    
    distancia_run = 0; distancia_swimm = 0; distancia_other = 0;
    tiempo_run = 0; tiempo_swimm = 0; tiempo_other = 0;
    subida_run = 0; subida_swimm = 0; subida_other =0;
    cont_run = 0; cont_swimm = 0; cont_other = 0;
    for i in range(7):
        a = None
        current_date = inicio + timedelta(days=i)
        di_run = {
            "dia": nom[i],
            "fecha": current_date.day,
            "actividad": None,
            "is_today": (current_date ==today)
        }
        di_swimm = {
            "dia": nom[i],
            "fecha": current_date.day,
            "actividad": None,
            "is_today": (current_date == today)
        }
        di_other = {
            "dia": nom[i],
            "fecha": current_date.day,
            "actividad":  None,
            "is_today": (current_date == today)
        }
        for actividad in actividades:
            try:
                if(actividad.fecha.date() != current_date):
                    continue

                acums = actividad.acums
                sport = actividad.sport.lower()
                
                a = {
                    "id": actividad.id,
                    "sport": sport,
                    "link": (str(actividad.sport)).lower()+".svg" if actividad is not None else None,
                    "acums": acums
                }

                try:
                    dist = float(acums.get("acum_distancia", 0) or 0)
                except Exception:
                    dist = 0.0

                try:
                    tiempo = int(string_to_seconds(acums.get("acum_tiempo")) or 0)
                except Exception:
                    tiempo = 0

                try:
                    subida = float(acums.get("acum_subida", 0) or 0)
                except Exception:
                    subida = 0

                if(sport == "running"):
                    cont_run += 1;
                    distancia_run += dist
                    tiempo_run += tiempo
                    subida_run += subida
                    di_run["actividad"] = a
                    
                elif(sport == "swimming"):
                    cont_swimm += 1;
                    distancia_swimm += dist
                    tiempo_swimm += tiempo
                    subida_swimm += subida
                    di_swimm["actividad"] = a
                    
                elif(sport == "other"):
                    cont_other += 1;
                    distancia_other += dist
                    tiempo_other += tiempo
                    subida_other += subida
                    di_other["actividad"] = a
                else:
                    a: None
            except Exception as err:
                logger.exception("Error: ", err)

        semana.append({
            "dia": nom[i],
                    "fecha": (inicio + timedelta(days=i)).day,
                    "actividad":  a,
                    "is_today": ((inicio + timedelta(days=i)) == date.today())
        }) 

        d = {
            "d_run": di_run,
            "d_swimm": di_swimm,
            "d_other": di_other
        } 
        diario.append(d)
    
    
    semana_swimm.append(di_swimm)
    semana_other.append(di_other)
    
    tiempo_str_run = seconds_to_string(tiempo_run)
    tiempo_str_swimm = seconds_to_string(tiempo_swimm)
    tiempo_str_other = seconds_to_string(tiempo_other)
    #semana_sport.append({"semana_run": semana_run, "semana_swimm": semana_swimm, "semana_other": semana_other})
    #print(semana_sport)

    total_semana = {"total_activities_run": cont_run,"total_distancia_run": round(distancia_run, 2), "total_tiempo_run": tiempo_str_run, "total_subida_run": floor(subida_run),
              "total_acivities_swimm": cont_swimm,"total_distancia_swimm": round(distancia_swimm, 2), "total_tiempo_swimm": tiempo_str_swimm, "total_subida_swimm": floor(subida_swimm),
               "total_activities_other": cont_other, "total_distancia_other": round(distancia_other, 2), "total_tiempo_other": tiempo_str_other, "total_subida_other": floor(subida_other)}
    
    return(diario, semana, total_semana)


def crear_mes(mes, year, user):
    if(mes == 12):
        next_mes = 1
        next_year = year + 1
    else:
        next_mes = mes + 1
        next_year = year
    actividades_mes = Activity.objects.filter(fecha__month=mes, fecha__year=year, usuario=user).order_by("fecha")
    activ_mes = [*actividades_mes]
    primero_de_mes = date(year,mes, 1)
    ultimo_de_mes = date(next_year, next_mes , 1 ) - timedelta(days=1)
    
    primer_lunes = primero_de_mes - timedelta(days = primero_de_mes.weekday())
    ultimo_domingo = ultimo_de_mes +  timedelta(days = 6 - ultimo_de_mes.weekday())
    rango = (ultimo_domingo - primer_lunes).days + 1
    semanas = int((rango )  / 7)
    try:
        weeks = []
        for w in range( semanas):
            week = []
            for d in range(7):
                a = None
                dia_calendario = {
                    "dia": None,
                    "acts_dia": [],
                    "actual_month": True,
                }
                dia = primer_lunes + timedelta(days = w * 7 + d)
                acts_dia = []
                while(len(activ_mes) > 0 and dia.day == activ_mes[0].fecha.day):
                    a = activ_mes[0]
                    activ_mes.pop(0)
                    acts_dia.append(a)
                dia_calendario["dia"] = dia
                dia_calendario["acts_dia"] = acts_dia
                dia_calendario["actual_month"] = (dia.month == mes)
                week.append(dia_calendario)
            weeks.append(week)
        
        
        
        for week in weeks:
            resumen = {
            "cont":0,
            "suma_dist":0,
            "suma_tiempo": 0
            }
            cont = 0
            acum_tiempo = 0
            acum_dist = 0
            lun = week[0]["dia"].isocalendar()
            
            for day in week:
                if(day['acts_dia']):
                   for act_day in day['acts_dia']:
                       cont += 1
                       acum_dist += float(act_day.acums["acum_distancia"])
                       acum_tiempo += string_to_seconds(act_day.acums["acum_tiempo"])
            resumen["cont"] = cont
            resumen["suma_dist"] = round(acum_dist,2)
            resumen['suma_tiempo'] = seconds_to_string(acum_tiempo) if acum_tiempo != 0 else '--'
            week.append(resumen)
            #print(week)

    except Exception as error:
        logger.error("Error:", error)
    return weeks

def crear_dias_mes(mes, year, user):
    activities = Activity.objects.filter(fecha__month=mes, fecha__year=year, usuario=user)
    dias = calendar.monthrange(year, mes)[1]
    dias_mes = []
    
    for i in range(1,dias + 1):
        d = {
        "dia": 0,
        "distancia": 0
        }
        a = next((actividad.acums.get("acum_distancia") for actividad in activities if actividad.fecha.day == int(i)), 0)
        d["dia"] = i
        d["distancia"] = round((float(a)), 2)
        dias_mes.append(d)
    return dias_mes

def crear_year(year, user):
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    activities = Activity.objects.filter(fecha__year=year, usuario=user)
    year_by_mes = []
    year_tots = None
    acum_dist_tots = 0
    acum_tiempo_tots = 0
    for mes in range(1,13):
        activities_mes = activities.filter(fecha__month=mes)
        count = activities_mes.count()
        acum_dist = 0
        acum_tiempo = 0
        for act_mes in activities_mes:
            acum_dist += float(act_mes.acums.get("acum_distancia"))
            acum_dist_tots += float(act_mes.acums.get("acum_distancia"))
            acum_tiempo += string_to_seconds(act_mes.acums.get("acum_tiempo"))
            acum_tiempo_tots += string_to_seconds(act_mes.acums.get("acum_tiempo"))
        data_mes = {
            "year": int(year),
            "prev_year": int(year) - 1,
            "next_year": int(year) + 1,
            "mes_num": mes,
            "mes": meses[mes - 1],
            "distancia_mes": round(acum_dist, 2),
            "tiempo_mes": seconds_to_string(acum_tiempo),
            "count": count
        }
        year_by_mes.append(data_mes)
    year_tots = {
        "acum_dist_tots": round(acum_dist_tots, 2),
        "acum_tiempo_tots": seconds_to_string(acum_tiempo_tots).split('h')[0]
    }
    return year_by_mes, year_tots