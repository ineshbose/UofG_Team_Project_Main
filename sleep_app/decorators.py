from django.shortcuts import redirect


def staff_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_staff:
            print("you have to be a staff member")
            return redirect('sleep_app:main_form_page')
        print(request.user, " is a staff:", request.user.is_staff)
        return view_func(request, *args, **kwargs)

    return wrapper_func