
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("activities", views.activities, name="activities"),
    path("activities/agregar", views.add_activity, name="add_activity"),
    path("activities/delete/<int:activity_id>", views.delete_activity, name="delete_activity"),
    path("activity/<int:activity_id>", views.activity_view, name="activity_view"),
    
]
