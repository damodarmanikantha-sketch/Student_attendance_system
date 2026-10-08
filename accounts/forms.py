from django.contrib.auth.forms import UserCreationForm
from .models import User


class StudentSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "face_image",
        ]
        
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg rounded-pill",
            "placeholder": "Enter Username"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-control-lg rounded-pill",
            "placeholder": "Enter Password"
        })
    )