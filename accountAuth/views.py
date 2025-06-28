from django.shortcuts import render, redirect
from .forms import CustomLoginForm, CustomSignupForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

@csrf_exempt
def login_view(request):
    form = CustomLoginForm(request.POST or None)
    embedded = request.GET.get('embedded') == 'true' or request.POST.get('embedded') == 'true'

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('finance')  # or return HttpResponse("OK") if modal logic is needed
            else:
                form.add_error(None, "Invalid email or password")

    if embedded:
        return render(request, 'partials/login_form.html', {'form': form})
    return render(request, 'account/login.html', {'form': form})

def signup_view(request):
    form = CustomSignupForm(request.POST or None)
    embedded = request.GET.get('embedded') == 'true' or request.POST.get('embedded') == 'true'

    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            auth_login(request, user)
            return redirect('custom-login')  # or return HttpResponse("OK") if modal logic is needed

    if embedded:
        return render(request, 'partials/signup_form.html', {'form': form})
    return render(request, 'account/signup.html', {'form': form})

def logout(request):
    if request.method == 'POST':
        auth_logout(request)
    return redirect('custom-login')