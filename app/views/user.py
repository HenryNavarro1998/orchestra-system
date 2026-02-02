from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django import forms
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from app.models import AcademicPeriod, DetailAcademicInscription

@login_required
def home(request):

    current_academic_period = AcademicPeriod.objects.filter(is_active=True).first()
    aggregate_options = {
        "wind": Count("id", filter=Q(id_instrument__category="Wind")),
        "string": Count("id", filter=Q(id_instrument__category="String")),
        "percussion": Count("id", filter=Q(id_instrument__category="Percussion")),
        "all": Count("id")
    }
    
    total_by_category = DetailAcademicInscription.objects.filter(id_academic_period__is_active=True).aggregate(**aggregate_options)

    # Acceso a los resultados
    context = {
        "wind_students": total_by_category["wind"],
        "string_students": total_by_category["string"],
        "percussion_students": total_by_category["percussion"],
        "all_students": total_by_category["all"],
    }

    return render(request, "home.html", context)


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label = "",
        widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo institucional',
            'required': 'required'
        })
    )
    password = forms.CharField(
        label = "",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'required': 'required'
        })
    )

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('app:home')  

def profile(request):
    username = "Génova Castillo"
    return render(request, 'profile.html', {
        'username': username
    }) 

def signout(request):
    logout(request)
    return redirect('app:login')
    

    