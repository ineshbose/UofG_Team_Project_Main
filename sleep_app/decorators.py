from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages


def unauthenticated_user(view_func):

    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info('you are already logged in')
            return redirect('sleep_app:main_form_page')
        return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator