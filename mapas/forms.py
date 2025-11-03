from django import forms
from .models import Activity, User

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["nombre", "descripcion", "archivo_tcx", "url_archivo"]

class LoginForm(forms.Form):
        username= forms.CharField(max_length=150)
        password = forms.CharField(widget=forms.PasswordInput)

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "password", "email"]