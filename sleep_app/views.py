import csv
import json
import random
import urllib

import pandas as pd
import plotly.graph_objs as go

from django.http import HttpResponse
from django.contrib import auth, messages
from django.contrib.auth import authenticate
from next_prev import next_in_order, prev_in_order
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import AuthenticationForm

from . import models
from . import forms
from . import decorators


def index(request):
    return redirect("sleep_app:main_form_page")


@decorators.staff_required
def map(request):
    selected_symptom = None
    latitude = []
    longitude = []
    popup = []
    temp = models.Symptom.objects.all()
    s = []

    for symptom in temp:
        if len(s) != 0:
            if symptom not in s:
                s.append(symptom)
        else:
            s.append(symptom)

    if request.method == "POST":
        selected_symptom = request.POST.get("dropdown1")

    if selected_symptom is None:
        if models.Person.objects.all():
            for person in models.Person.objects.all():
                if person.gps_location:
                    latitude.append(person.gps_location.split(",")[0])
                    longitude.append(person.gps_location.split(",")[1])
                    popup.append(person.id)
                elif person.db_location:
                    latitude.append(person.db_location.split(",")[0])
                    longitude.append(person.db_location.split(",")[1])
                    popup.append(person.id)

    else:
        for person in models.Person.objects.all():
            answers = person.answerset_set.all()
            for a in answers:
                if str(a.response.symptom) == selected_symptom and (
                    (a.response.text_response)
                    or (a.response.bool_response == True)
                    or (a.response.scale_response)
                ):
                    if person.gps_location:
                        latitude.append(person.gps_location.split(",")[0])
                        longitude.append(person.gps_location.split(",")[1])
                        popup.append(str(a.response) + "  ID:" + str(person.id))
                    elif person.db_location:
                        latitude.append(person.db_location.split(",")[0])
                        longitude.append(person.db_location.split(",")[1])
                        popup.append(str(a.response) + "  ID:" + str(person.id))

    fig = go.Figure(
        data=go.Scattergeo(
            lon=longitude,
            lat=latitude,
            text=popup,
            mode="markers",
            marker=dict(
                color="red",
                opacity=0.8,
                symbol="circle",
                line=dict(width=1, color="rgba(102, 102, 102)"),
                cmin=0,
                size=5,
                cmax=5,
            ),
        )
    )

    fig2 = go.Figure(
        data=go.Scattergeo(
            lon=longitude,
            lat=latitude,
            text=popup,
            mode="markers",
            marker=dict(
                color="red",
                opacity=0.8,
                symbol="circle",
                line=dict(width=1, color="rgba(102, 102, 102)"),
                cmin=0,
                size=5,
                cmax=5,
            ),
        )
    )

    fig.update_geos(showcountries=True)
    fig2.update_geos(showcountries=True, scope="africa")
    plot_div = fig.to_html(full_html=False, default_height=600, default_width=1200)
    plot_div2 = fig2.to_html(full_html=False, default_height=700, default_width=1200)
    context = {
        "figure": fig,
        "plot_div": plot_div,
        "plot_div2": plot_div2,
        "all_symptoms": s,
        "selected_symptom": selected_symptom,
    }
    return render(request, "sleep_app/map.html", context)


def create_person_and_id(request):
    """
    [Helper Function]
    Generates a person object with a unique random id whenever the first page of a question is visited.
    """
    new_id = int(random.uniform(0, 1000000))
    while models.Person.objects.filter(id=new_id).count() > 0:
        new_id = int(random.uniform(0, 1000000))
    person = models.Person(id=new_id)
    person.save()
    request.session["person"] = person.id


def increase_log_amount(request):
    request.session["log_amount"] = request.session.get("log_amount", 0) + 1


def form(request):
    if request.method == "POST":
        if "cancel" in request.POST:
            current_person = models.Person.objects.get(id=request.session["person"])
            current_person.delete()
            del request.session["person"]

    context_dict = {
        "first_symptom_mop": models.Symptom.objects.filter(symptom_type="MOP").first(),
        "first_symptom_hcw": models.Symptom.objects.filter(symptom_type="HCW").first(),
        "first_symptom_eov": models.Symptom.objects.filter(symptom_type="EOV").first(),
    }

    #   this means that that the session will expire in *24h*, not at the beginning of the next day
    #   1209600 is the default return value
    #   (https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-SESSION_COOKIE_AGE)
    if request.session.get_expiry_age() == 1209600:
        request.session.set_expiry(60 * 60 * 24)
    context_dict["log_amount"] = request.session.get("log_amount", 0)
    return render(request, "sleep_app/form.html", context_dict)


def get_response_form(resp_type):
    """
    [Helper Function]
    Returns the response form for a given answer type.
    """
    return {
        "bool": forms.YesNoResponseForm,
        "text": forms.TextResponseForm,
        "int": forms.ScaleResponseForm,
    }.get(resp_type)


def get_response_answer(resp_type):
    """
    [Helper Function]
    Returns the response answer for a given answer type.
    """
    return {
        "bool": resp_type.response.bool_response,
        "text": resp_type.response.text_response,
        "int": resp_type.response.scale_response,
    }.get(resp_type.response.symptom.answer_type, "")


def symptom_question(request, symptom_name_slug):
    if request.method == "GET":
        context_dict = {}
        try:
            symptom = models.Symptom.objects.get(slug=symptom_name_slug)
            context_dict["symptom"] = symptom
            context_dict["prev_symptom"] = (
                None
                if symptom
                == models.Symptom.objects.filter(
                    symptom_type=symptom.symptom_type
                ).first()
                else prev_in_order(symptom)
            )
            context_dict["response_form"] = get_response_form(symptom.answer_type)()

        except models.Symptom.DoesNotExist:
            context_dict["symptom"] = context_dict["response_form"] = None

        return render(request, "sleep_app/symptom_question.html", context=context_dict)

    elif request.method == "POST":
        # clicking on the link to the form sends a POST request to this page. That causes a new person object to be generated
        if "first" in request.POST:
            create_person_and_id(request)
            return redirect(
                reverse(
                    "sleep_app:symptom_form",
                    kwargs={"symptom_name_slug": symptom_name_slug},
                )
            )
        else:
            try:
                symptom = models.Symptom.objects.get(slug=symptom_name_slug)
                response_form = get_response_form(symptom.answer_type)(request.POST)

                if response_form.is_valid():
                    if symptom.answer_type == "bool":
                        response = models.Response(
                            symptom=symptom,
                            bool_response=response_form.cleaned_data["bool_response"],
                        )
                    elif symptom.answer_type == "text":
                        response = models.Response(
                            symptom=symptom,
                            text_response=response_form.cleaned_data["text_response"],
                        )
                    else:
                        response = models.Response(
                            symptom=symptom,
                            scale_response=response_form.cleaned_data["scale_response"],
                        )
                response.save()

            # for some reason we got here through a page with an invalid symptom slug. Should never happen.
            except models.Symptom.DoesNotExist:
                print(f"ERROR: Symptom with slug {symptom_name_slug} does not exist.")
                return redirect("sleep_app:main_form_page")

            try:
                current_person = models.Person.objects.get(id=request.session["person"])
                # user has answered this question before (used the "previous" button). Delete the old answer
                old_answer = current_person.answerset_set.filter(
                    response__symptom=symptom
                )
                if old_answer.count() > 0:
                    old_answer.first().delete()
                answer_set = models.AnswerSet(person=current_person, response=response)
                answer_set.save()

            except models.Person.DoesNotExist:
                print(
                    f"ERROR: Person with id {request.session['person']} does not exist"
                )
                return redirect("sleep_app:main_form_page")

            return redirect(
                "sleep_app:location"
                if symptom
                == models.Symptom.objects.filter(
                    symptom_type=symptom.symptom_type
                ).last()
                else reverse(
                    "sleep_app:symptom_form",
                    kwargs={"symptom_name_slug": next_in_order(symptom).slug},
                )
            )


def location(request):
    if request.method == "POST" and "person" in request.session:
        try:
            current_person = models.Person.objects.get(id=request.session["person"])
            if "lat" in request.POST:
                if request.POST["lat"] != "no-permission":
                    current_person.gps_location = ",".join(
                        [request.POST["lat"], request.POST["long"]]
                    )
                    current_person.save()
                    increase_log_amount(request)

            elif "location" in request.POST:
                x = json.loads(
                    urllib.request.urlopen(
                        "https://nominatim.openstreetmap.org/search?"
                        f'{urllib.parse.urlencode({"q": request.POST["location"], "format": "geojson"})}'
                    )
                    .read()
                    .decode()
                )
                if len(x["features"]) > 0:
                    long, lat = x["features"][0]["geometry"]["coordinates"][:2]
                    current_person.db_location = f"{lat},{long}"
                    increase_log_amount(request)
                current_person.location_text = request.POST["location"]
                current_person.save()

        except models.Person.DoesNotExist:
            print(f"ERROR: Person with id {request.session['person']} does not exist")

        return redirect("sleep_app:success")

    return render(request, "sleep_app/location.html", context={})


@decorators.staff_required
def table(request):
    headers = [
        "Person ID",
        "Date",
        "Location",
        "Map Database Coordinates",
        "GPS Coordinates",
        *list(dict.fromkeys(symptom.name for symptom in models.Symptom.objects.all())),
    ]

    data = [
        {
            "Person ID": person.id,
            "Date": person.date.strftime("%d/%m/%Y, %H:%M:%S"),
            "Location": person.location_text,
            "Map Database Coordinates": person.db_location,
            "GPS Coordinates": person.gps_location,
            **{
                symptom.name: ""
                for symptom in models.Symptom.objects.filter(name__in=headers)
            },
            **{
                a.response.symptom.name: get_response_answer(a)
                for a in person.answerset_set.filter(
                    response__symptom__name__in=headers
                )
            },
        }
        for person in models.Person.objects.all().order_by("date")
    ]

    return render(request, "sleep_app/table.html", {"headers": headers, "data": data})


@decorators.login_not_required
def login(request):
    errormsg = " "
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            authenticate(username=user.username, password=user.password)
            auth.login(request, user)
            return redirect("sleep_app:main_form_page")
        else:
            errormsg = "Wrong username or password"
    else:
        form = AuthenticationForm()
    context = {"form": form, "errormsg": errormsg}
    return render(request, "sleep_app/login.html", context)


@decorators.login_not_required
def register(request):
    form = forms.RegisterForm()
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get("username")
            return redirect("sleep_app:login")
        else:
            return render(request, "sleep_app/register.html", {"form": form})

    return render(request, "sleep_app/register.html", {"form": form})


@decorators.login_required
def logout(request):
    auth.logout(request)
    return redirect("sleep_app:main_form_page")


def success(request):
    try:
        person = models.Person.objects.get(id=request.session["person"])
    except models.Person.DoesNotExist:
        person = None
    return render(request, "sleep_app/success.html", {"person":person})


@decorators.staff_required
def export_csv(request):
    filename, content_type = f"responses.csv", "text/csv"
    response = HttpResponse(content_type=content_type)
    headers = [
        "Person ID",
        "Date",
        "Location",
        "Map Database Coordinates",
        "GPS Coordinates",
        *list(dict.fromkeys(symptom.name for symptom in models.Symptom.objects.all())),
    ]

    writer = csv.DictWriter(response, fieldnames=headers)
    writer.writeheader()
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer.writerows(
        [
            {
                "Person ID": person.id,
                "Date": person.date.strftime("%d/%m/%Y, %H:%M:%S"),
                "Location": person.location_text,
                "Map Database Coordinates": person.db_location,
                "GPS Coordinates": person.gps_location,
                **{
                    symptom.name: ""
                    for symptom in models.Symptom.objects.filter(name__in=headers)
                },
                **{
                    a.response.symptom.name: get_response_answer(a)
                    for a in person.answerset_set.filter(
                        response__symptom__name__in=headers
                    )
                },
            }
            for person in models.Person.objects.all().order_by("date")
        ]
    )

    return response
