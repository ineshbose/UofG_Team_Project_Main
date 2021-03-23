from django.shortcuts import redirect


def staff_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        return (
            view_func(request, *args, **kwargs)
            if request.user.is_staff
            else redirect("sleep_app:main_form_page")
        )

    return wrapper_func


def login_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        return (
            view_func(request, *args, **kwargs)
            if request.user.is_authenticated
            else redirect("sleep_app:main_form_page")
        )

    return wrapper_func


def login_not_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        return (
            view_func(request, *args, **kwargs)
            if not request.user.is_authenticated
            else redirect("sleep_app:main_form_page")
        )

    return wrapper_func
