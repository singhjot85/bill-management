from bma.core.constants import APIRequestMethods as Method
from bma.core.forms import BaseCustomerForm, CustomerForm
from bma.core.models import BaseUserModel

from django.contrib.auth import login, authenticate
from django.http import HttpRequest
from django.shortcuts import render, redirect

AUTH_TEMPLATE = "viewset_templates/auth.html"
ERROR_TEMPLATE = "viewset_templates/404.html"
AUTH_REDIRECT = "admin"

def auth_view(request: HttpRequest, *args, **kwargs):
    err_msg = None

    if _is_authenticated(request):
        return redirect(AUTH_REDIRECT)
    
    req_method = request.method.upper()
    
    if req_method == Method.GET.value:
        form = BaseCustomerForm()
        mode = "login"

        if request.GET.get("mode", None) == "register":
            form = CustomerForm()
            mode = "register"

        context={
            "form": form,
            "mode": mode
        }
        return render(request, AUTH_TEMPLATE, context=context)

    if req_method == Method.POST.value:
        data = request.POST
        username = data.get("username", None)
        password = data.get("password", None)

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(AUTH_REDIRECT)
        
        form = CustomerForm(request.POST)
        if form.is_valid():
            _create_user(data)
            return redirect(AUTH_REDIRECT)

    return render(request, ERROR_TEMPLATE, context={"message": err_msg})

def _is_authenticated(request: HttpRequest):
    session_valid = (
        request.session.session_key
        and request.session.exists(request.session.session_key)
    )
    user_valid = (
        request.user.is_authenticated
    )
    return session_valid and user_valid

def _create_user(data: dict):
    username=data.get("username")
    password=data.get("password")
    user: BaseUserModel = BaseUserModel.objects.create(username)
    user.set_password(password)

    NON_UPDATABLE_ATTRS=['username', 'password', 'is_active', 'is_superuser']
    for attr, val in data.items():
        if attr in NON_UPDATABLE_ATTRS:
            continue
        if hasattr(user, str(attr)):
            setattr(user, attr, val)
    user.save()