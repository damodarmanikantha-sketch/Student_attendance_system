from django.shortcuts import render, redirect
from .forms import StudentSignupForm,LoginForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


def student_signup(request):
    if request.method == "POST":
        form = StudentSignupForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("signup_success")

    else:
        form = StudentSignupForm()

    return render(request, "accounts/signup.html", {"form": form})

def signup_success(request):
    return render(request, "accounts/signup_success.html")

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm


def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()

        if not user.is_approved:
            form.add_error(None, "Your account is waiting for approval.")
        else:
            login(request, user)
            return redirect("home")

    return render(request, "accounts/login.html", {"form": form})


def home(request):
    return render(request, "accounts/home.html")


def user_logout(request):
    logout(request)
    return redirect("home")


@login_required 
def user_profile(request):
    return render(request, "accounts/user_profile.html")

from .models import User
@login_required
def student_approvals(request):
    if request.user.role != 'SUPERADMIN':
        return redirect("home")

    pending_students = User.objects.filter(role='STUDENT',is_approved=False,)

    return render(request,"accounts/student_approvals.html",{"pending_students": pending_students},)
    
@login_required
def approve_student(request, user_id):
    if request.user.role != 'SUPERADMIN':
        return redirect("home")

    if request.method == "POST":
        student = User.objects.get(id=user_id,role='STUDENT',)

        student.is_approved = True
        student.save()
    return redirect("student_approvals")