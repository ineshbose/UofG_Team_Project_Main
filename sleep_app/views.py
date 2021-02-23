import random
import json
import urllib

import plotly.graph_objs as go
import pandas as pd

from django.contrib import auth, messages
from django.shortcuts import render, redirect, reverse
from next_prev import next_in_order
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from sleep_app.decorators import staff_required

from . import models
from . import forms
from . import tables


@staff_required
def map(request):
    context_dict = {}
    return render(request, "sleep_app/map.html", context_dict)


def index(request):
    return redirect("sleep_app:main_form_page")


@staff_required
def map(request):
    df = pd.read_csv("static/sleep_app/testing2.csv")
    print(df)
    df["text"] = df["name"] + " - " + df["size"].astype(str) + " cases"

    selected_symptom = None
    latitude = []
    longitude = []
    id = []
    s = models.Symptom.objects.all()
    print(selected_symptom)
    if request.method == "POST":
        selected_symptom = request.POST.get("dropdown")

    if selected_symptom == None:
        for person in models.Person.objects.all():
            if person.location != None:
                latitude.append(person.location.split(",")[0])
                longitude.append(person.location.split(",")[1])
                id.append(person.id)
    else:
        for person in models.Person.objects.all():
            answers = person.answerset_set.all()
            print(person.id)
            print(person.location.split(",")[0])
            print(person.location.split(",")[1])
            for a in answers:
                if (
                    str(a.response.symptom) == selected_symptom
                    and a.response.answer == True
                ):
                    latitude.append(person.location.split(",")[0])
                    longitude.append(person.location.split(",")[1])
                    id.append(person.id)

    fig = go.Figure(
        data=go.Scattergeo(
            lon=longitude,
            lat=latitude,
            text=id,
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
            text=id,
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

    fig.update_geos(showcountries=True)  # Automatically zoom into the zone of interest
    fig2.update_geos(
        showcountries=True, scope="africa"
    )  # Automatically zoom into the zone of interest
    plot_div = fig.to_html(full_html=False, default_height=700, default_width=1000)
    plot_div2 = fig2.to_html(full_html=False, default_height=700, default_width=1000)
    context = {
        "plot_div": plot_div,
        "plot_div2": plot_div2,
        "all_symptoms": s,
        "selected_symptom": selected_symptom,
    }
    return render(request, "sleep_app/map.html", context)


# helper function. Generates a person object with a unique random id whenever the first page of a question is visited.
def create_person_and_id(request):
    new_id = int(random.uniform(0, 1000000))
    # to prevent id collision
    while models.Person.objects.filter(id=new_id).count() > 0:
        new_id = int(random.uniform(0, 1000000))
    person = models.Person(id=new_id)
    person.save()
    request.session["person"] = person.id


def increase_log_amount(request):
    request.session["log_amount"] = request.session.get("log_amount", 0) + 1


# the view for the page that takes you to the questions
def form(request):
    if request.method == "POST":
        if "cancel" in request.POST:
            current_person = models.Person.objects.get(id=request.session["person"])
            current_person.delete()
            del request.session["person"]

    first_symptom_mop = models.Symptom.objects.filter(symptom_type="MOP").first()
    first_symptom_hcw = models.Symptom.objects.filter(symptom_type="HCW").first()
    first_symptom_eov = models.Symptom.objects.filter(symptom_type="EOV").first()
    context_dict = {
        "first_symptom_mop": first_symptom_mop,
        "first_symptom_hcw": first_symptom_hcw,
        "first_symptom_eov": first_symptom_eov,
    }

    #   this means that that the session will expire in *24h*, not at the beginning of the next day
    #   1209600 is the default return value
    #   (https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-SESSION_COOKIE_AGE)
    if request.session.get_expiry_age() == 1209600:
        request.session.set_expiry(60 * 60 * 24)
    context_dict["log_amount"] = request.session.get("log_amount", 0)
    return render(request, "sleep_app/form.html", context_dict)


# the view for the page that asks about a specific symptom
def symptom_question(request, symptom_name_slug):
    if request.method == "GET":
        context_dict = {}
        try:
            symptom = models.Symptom.objects.get(slug=symptom_name_slug)
            context_dict["symptom"] = symptom
            # need to pass the proper type of response object to the template, depending on what type of response is needed
            if symptom.answer_type == "bool":
                response_form = forms.YesNoResponseForm()
            elif symptom.answer_type == "text":
                response_form = forms.TextResponseForm()
            else:
                response_form = forms.ScaleResponseForm()
            context_dict["response_form"] = response_form
        except models.Symptom.DoesNotExist:
            context_dict["symptom"] = context_dict["response_form"] = None
        return render(request, "sleep_app/symptom_question.html", context=context_dict)

    elif request.method == "POST":
        # clicking on the link to the form sends a POST request to this page. That causes a new person object to be generated
        if "first" in request.POST:
            try:
                create_person_and_id(request)
                return redirect(
                    reverse(
                        "sleep_app:symptom_form",
                        kwargs={"symptom_name_slug": symptom_name_slug},
                    )
                )
            except models.Person.DoesNotExist:
                print("Error: could not find symptom")
        else:
            try:
                symptom = models.Symptom.objects.get(slug=symptom_name_slug)
                if symptom.answer_type == "bool":
                    response_form = forms.YesNoResponseForm(request.POST)
                    if response_form.is_valid():
                        response = models.Response(
                            symptom=symptom,
                            bool_response=response_form.cleaned_data["bool_response"],
                        )
                        response.save()
                elif symptom.answer_type == "text":
                    response_form = forms.TextResponseForm(request.POST)
                    if response_form.is_valid():
                        response = models.Response(
                            symptom=symptom,
                            text_response=response_form.cleaned_data["text_response"],
                        )
                        response.save()
                else:
                    response_form = forms.ScaleResponseForm(request.POST)
                    if response_form.is_valid():
                        response = models.Response(
                            symptom=symptom,
                            scale_response=response_form.cleaned_data["scale_response"],
                        )
                        response.save()
            # for some reason we got here through a page with an invalid symptom slug. Should never happen.
            except models.Symptom.DoesNotExist:
                print(
                    "ERROR: Symptom with slug {slug} does not exist.".format(
                        slug=symptom_name_slug
                    )
                )
                return redirect("sleep_app:main_form_page")

            try:
                current_person = models.Person.objects.get(id=request.session["person"])
                answer_set = models.AnswerSet(person=current_person, response=response)
                answer_set.save()

            except models.Person.DoesNotExist:
                print(
                    "ERROR: Person with id {id} does not exist".format(
                        id=request.session["person"]
                    )
                )
                return redirect("sleep_app:main_form_page")

            if (
                symptom
                == models.Symptom.objects.filter(
                    symptom_type=symptom.symptom_type
                ).last()
            ):
                return redirect("sleep_app:location")
            else:
                next_symptom = next_in_order(symptom)
                return redirect(
                    reverse(
                        "sleep_app:symptom_form",
                        kwargs={"symptom_name_slug": next_symptom.slug},
                    )
                )


def location(request):
    context_dict = {"browser_location": True}
    if request.method == "POST":
        try:
            current_person = models.Person.objects.get(id=request.session["person"])
            if "lat" in request.POST:
                if request.POST["lat"] != "no-permission":
                    current_person.location = ",".join(
                        [request.POST["lat"], request.POST["long"]]
                    )
                    current_person.save()
                    increase_log_amount(request)

            elif "location" in request.POST:
                context_dict = {"browser_location": False}
                query = {"q": request.POST["location"], "format": "geojson"}
                encode = urllib.parse.urlencode(query)
                url = "https://nominatim.openstreetmap.org/search?" + encode
                data = urllib.request.urlopen(url).read().decode()
                x = json.loads(data)
                if len(x["features"]) != 0:
                    print(x["features"][0]["geometry"]["coordinates"])
                    context_dict["success"] = True
                    coords = ",".join(
                        [
                            str(x["features"][0]["geometry"]["coordinates"][1]),
                            str(x["features"][0]["geometry"]["coordinates"][0]),
                        ]
                    )
                    context_dict["lat"] = x["features"][0]["geometry"]["coordinates"][1]
                    context_dict["long"] = x["features"][0]["geometry"]["coordinates"][0]
                    current_person.location = coords
                    increase_log_amount(request)
                current_person.location_text = request.POST["location"]
                current_person.save()

        except models.Person.DoesNotExist:
            print(
                "ERROR: Person with id {id} does not exist".format(
                    id=request.session["person"]
                )
            )

    return render(request, "sleep_app/location.html", context=context_dict)


# Normally it would be easier to just let the PersonTable class use Person.objects.all() (as shown in the django-tables2
# tutorial). However django-tables2 does not make it possible to put the items in the response many to many field into the
# appropriate symptom columns. So this generates a list of dicts, where each dict represents one person's data in the proper
# format. The disadvantage of doing it this way is that it is rather slow (when using the cloud database)
# so a better solution might be needed later.


@staff_required
def table(request):
    data = []
    for p in models.Person.objects.all():
        info = {"id": p.id, "date": p.date, "location": p.location, "location_text":p.location_text}
        answers = p.answerset_set.all()
        for a in answers:
            if a.response.symptom.answer_type == "bool":
                info[a.response.symptom.name] = a.response.bool_response
            elif a.response.symptom.answer_type == "text":
                info[a.response.symptom.name] = a.response.text_response
            else:
                info[a.response.symptom.name] = a.response.scale_response
        data.append(info)

    person_table = tables.PersonTable(data)
    return render(request, "sleep_app/table.html", {"table": person_table})


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():

            user = form.get_user()
            print(user.is_staff)
            print(user)
            authenticate(username=user.username, password=user.password)
            auth.login(request, user)
            return redirect("sleep_app:main_form_page")
    else:
        form = AuthenticationForm()
    context = {"form": form}
    return render(request, "sleep_app/login.html", context)


def register(request):
    form = forms.RegisterForm()
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            print("register success")
            form.save()
            user = form.cleaned_data.get("username")
            return redirect("sleep_app:login")
        else:
            print(form.cleaned_data)
            print(form.errors)
            return render(request, "sleep_app/register.html", {"form": form})

    return render(request, "sleep_app/register.html", {"form": form})


def logout(request):
    auth.logout(request)
    print("logout success")
    return redirect("sleep_app:main_form_page")
