from django.shortcuts import render
from sleep_app.models import (
    Symptom,
    Person,
    Response,
    YesNoResponse,
    TextResponse,
    ScaleResponse,
)
from sleep_app.forms import YesNoResponseForm, TextResponseForm, ScaleResponseForm
import random
from django.shortcuts import redirect, reverse
from urllib import parse
from next_prev import next_in_order
import urllib
import json
from django.shortcuts import render

import plotly.graph_objs as go
import pandas as pd
from .tables import *


def map(request):
    context_dict = {}

    return render(request, 'sleep_app/map.html', context_dict)


def index(request):
    return redirect("sleep_app:main_form_page")


def map(request):
    df = pd.read_csv('testing2.csv')
    print(df)
    df['text'] = df['name'] + ' - ' + df['size'].astype(str) + ' cases'

    selected_symptom = None
    latitude = []
    longitude = []
    id = []
    s = Symptom.objects.all()
    print(selected_symptom)
    if request.method == "POST":
        selected_symptom = request.POST.get("dropdown")

    if selected_symptom == None:
        for person in Person.objects.all():
            if person.location != None:
                latitude.append(person.location.split(",")[0])
                longitude.append(person.location.split(",")[1])
                id.append(person.id)
    else:
        for person in Person.objects.all():
            if person.response.exists():
                print(person.id)
                print(person.location.split(",")[0])
                print(person.location.split(",")[1])
                for response in person.response.all():
                    if str(response.symptom) == selected_symptom and response.answer == True:
                        latitude.append(person.location.split(",")[0])
                        longitude.append(person.location.split(",")[1])
                        id.append(person.id)

    fig = go.Figure(data=go.Scattergeo(
        lon=longitude,
        lat=latitude,
        text=id,
        mode='markers',
        marker=dict(
            color='red',
            opacity=0.8,
            symbol='circle',
            line=dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            cmin=0,
            size=5,
            cmax=5,
        )))

    fig2 = go.Figure(data=go.Scattergeo(
        lon=longitude,
        lat=latitude,
        text=id,
        mode='markers',
        marker=dict(
            color='red',
            opacity=0.8,
            symbol='circle',
            line=dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            cmin=0,
            size=5,
            cmax=5,
        )))

    fig.update_geos(showcountries=True)  # Automatically zoom into the zone of interest
    fig2.update_geos(showcountries=True, scope='africa')  # Automatically zoom into the zone of interest
    plot_div = fig.to_html(full_html=False, default_height=700, default_width=1000)
    plot_div2 = fig2.to_html(full_html=False, default_height=700, default_width=1000)
    context = {'plot_div': plot_div,
               'plot_div2': plot_div2,
               'all_symptoms': s,
               'selected_symptom': selected_symptom,
               }
    return render(request, "sleep_app/map.html", context)


# helper function. Generates a person object with a unique random id whenever the first page of a question is visited.
def create_person_and_id(request):
    new_id = int(random.uniform(0, 1000000))
    # to prevent id collision
    while Person.objects.filter(id=new_id).count() > 0:
        new_id = int(random.uniform(0, 1000000))
    person = Person(id=new_id)
    person.save()
    request.session["person"] = person.id


def increase_log_amount(request):
    request.session["log_amount"] = request.session.get("log_amount", 0) + 1


# the view for the page that takes you to the questions
def form(request):
    if request.method == "POST":
        if "cancel" in request.POST:
            current_person = Person.objects.get(id=request.session["person"])
            current_person.delete()
            del request.session["person"]

    first_symptom_mop = Symptom.objects.filter(symptom_type="MOP").first()
    first_symptom_hcw = Symptom.objects.filter(symptom_type="HCW").first()
    first_symptom_eov = Symptom.objects.filter(symptom_type="EOV").first()
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
            symptom = Symptom.objects.get(slug=symptom_name_slug)
            context_dict["symptom"] = symptom
            # need to pass the proper type of response object to the template, depending on what type of response is needed
            if symptom.answer_type == "bool":
                response_form = YesNoResponseForm()
            elif symptom.answer_type == "text":
                response_form = TextResponseForm()
            else:
                response_form = ScaleResponseForm()
            context_dict["response_form"] = response_form
        except Symptom.DoesNotExist:
            context_dict["symptom"] = context_dict["response_form"] = None
        return render(request, 'sleep_app/symptom_question.html', context=context_dict)

    elif request.method == "POST":
        #clicking on the link to the form sends a POST request to this page. That causes a new person object to be generated
        if "first" in request.POST:
            try:
                create_person_and_id(request)
                return redirect(reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                          symptom_name_slug}))
            except Person.DoesNotExist:
                print("Error: could not find symptom")
        else:
            try:
                symptom = Symptom.objects.get(slug=symptom_name_slug)
                if symptom.answer_type == "bool":
                    response_form = YesNoResponseForm(request.POST)
                    if response_form.is_valid():
                        response = YesNoResponse(
                            symptom=symptom, answer=response_form.cleaned_data["answer"]
                        )
                        response.save()
                elif symptom.answer_type == "text":
                    response_form = TextResponseForm(request.POST)
                    if response_form.is_valid():
                        response = TextResponse(
                            symptom=symptom, answer=response_form.cleaned_data["answer"]
                        )
                        response.save()
                else:
                    response_form = ScaleResponseForm(request.POST)
                    if response_form.is_valid():
                        response = ScaleResponse(
                            symptom=symptom, answer=response_form.cleaned_data["answer"]
                        )
                        response.save()
            # for some reason we got here through a page with an invalid symptom slug. Should never happen.
            except Symptom.DoesNotExist:
                print(
                    "ERROR: Symptom with slug {slug} does not exist.".format(
                        slug=symptom_name_slug
                    )
                )
                return redirect("sleep_app:main_form_page")

            try:
                current_person = Person.objects.get(id=request.session["person"])
                current_person.response.add(response)
                current_person.save()

            except Person.DoesNotExist:
                print("ERROR: Person with id {id} does not exist".format(id=request.session['person']))
                return redirect("sleep_app:main_form_page")

            if symptom == Symptom.objects.filter(symptom_type=symptom.symptom_type).last():
                return redirect('sleep_app:location')
            else:
                next_symptom = next_in_order(symptom)
                return redirect(reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                              next_symptom.slug}))

def location(request):
    context_dict = {"browser_location": True}
    if request.method == 'POST':
        try:
            current_person = Person.objects.get(id=request.session['person'])
            if "lat" in request.POST:
                if request.POST["lat"] != "no-permission":
                    current_person.location = ",".join([request.POST["lat"], request.POST["long"]])
                    current_person.save()
                    increase_log_amount(request)

            elif "location" in request.POST:
                context_dict = {"browser_location": False}
                query = {"q": request.POST["location"],
                         "format": "geojson"
                         }
                encode = urllib.parse.urlencode(query)
                url = "https://nominatim.openstreetmap.org/search?" + encode
                data = urllib.request.urlopen(url).read().decode()
                x = json.loads(data)
                if len(x['features']) != 0:
                    print(x['features'][0]['geometry']['coordinates'])
                    context_dict["success"] = True
                    context_dict["location"] = ",".join(x['features'][0]['geometry']['coordinates'])
                    current_person.location = ",".join(x['features'][0]['geometry']['coordinates'])
                    current_person.save()
                    increase_log_amount(request)
                else:
                    context_dict["failure"] = True

        except Person.DoesNotExist:
            print("ERROR: Person with id {id} does not exist".format(id=request.session['person']))

    return render(request, 'sleep_app/location.html', context=context_dict)


# Normally it would be easier to just let the PersonTable class use Person.objects.all() (as shown in the django-tables2
# tutorial). However django-tables2 does not make it possible to put the items in the response many to many field into the
# appropriate symptom columns. So this generates a list of dicts, where each dict represents one person's data in the proper
# format. The disadvantage of doing it this way is that it is rather slow (when using the cloud database)
# so a better solution might be needed later.
def table(request):
    data = []
    for p in Person.objects.all():
        info = {"id": p.id, "date": p.date, "location": p.location}
        for r in p.response.all():
            info[r.symptom.name] = r.answer
        data.append(info)

    person_table = PersonTable(data)
    return render(request, "sleep_app/table.html", {"table": person_table})
