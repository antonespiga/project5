
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("profile_fisico/<int:user_id>", views.profile_fisico, name="profile_fisico"),
    path("activities", views.activities, name="activities"),
    path("activities/agregar", views.add_activity, name="add_activity"),
    path("activities/delete/<int:activity_id>", views.delete_activity, name="delete_activity"),
    path("activity/<int:activity_id>", views.activity_view, name="activity_view"),
    path("activities/semana", views.activities_semana, name="semana_actual"),
    path("activities/<int:year>/semana/<int:semana>", views.activities_semana, name="semana"),
    path("activities/mes", views.activities_mes, name="mes_actual"),
    path("activities/<int:year>/mes/<int:mes>", views.activities_mes, name="mes"),
    path("activities/year", views.activities_year, name="year_actual"),
    path("activities/year/<int:year>", views.activities_year, name="year"),
    path("activities/sorted/<str:campo>/<str:state>", views.activities_sorted, name="activities_sorted")
    
]
