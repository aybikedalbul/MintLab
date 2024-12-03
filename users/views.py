from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            return redirect('login')  # 'login' isimli bir URL tanımlı olmalı
    else:
        form = UserRegistrationForm()  # GET isteği için yeni bir form oluşturuluyor

    return render(request, 'register.html', {'form': form})  # Form her durumda döndürülür



def dashboard(request):
    return render(request, 'dashboard.html')