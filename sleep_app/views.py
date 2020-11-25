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
import datetime
from django.shortcuts import redirect
from urllib import parse
from next_prev import next_in_order, prev_in_order
from django.http import HttpResponse
from django.shortcuts import render

import plotly.offline as opy
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd


def index(request):
    return redirect("/form")


def map(request):
    df = pd.read_csv('testing2.csv')
    print(df)
    df['text'] = df['name'] + ' - ' + df['size'].astype(str) + ' cases'

    selected_symptom = None
    latitude = []
    longtitdue = []
    id = []
    s = Symptom.objects.all()
    print(selected_symptom)
    if request.method == "POST":
        selected_symptom = request.POST.get("dropdown")

    if selected_symptom == None:
        for person in Person.objects.all():
            if person.lat != None and person.long != None:
                latitude.append(person.lat)
                longtitdue.append(person.long)
                id.append(person.id)
    else:
        for person in Person.objects.all():
            if person.response.exists():
                print(person.id)
                print(person.lat)
                print(person.long)
                for response in person.response.all():
                    if str(response.symptom) == selected_symptom and response.answer == True:
                        latitude.append(person.lat)
                        longtitdue.append(person.long)
                        id.append(person.id)


    fig = go.Figure(data=go.Scattergeo(
        lon=longtitdue,
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
        lon=latitude,
        lat=longtitdue,
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



    fig.update_geos(showcountries=True) # Automatically zoom into the zone of interest
    fig2.update_geos(showcountries=True, scope='africa') # Automatically zoom into the zone of interest
    plot_div = fig.to_html(full_html=False, default_height=700, default_width=1000)
    plot_div2 = fig2.to_html(full_html=False, default_height=700, default_width=1000)
    context = {'plot_div': plot_div,
               'plot_div2': plot_div2,
               'all_symptoms': s,
               'selected_symtpom': selected_symptom,
               }
    return render(request, "sleep_app/map.html", context)


# helper function. Generates a person object with a unique random id whenever the first page of a question is visited.
def create_person_and_id(request):
    new_id = int(random.uniform(0, 1000000))
    #   to prevent id collision
    while request.session.get("person") == new_id:
        new_id = int(random.uniform(0, 1000000))
    person = Person(id=new_id)
    person.save()
    request.session["person"] = person.id


def increase_log_amount(request):
    request.session["log_amount"] = request.session.get("log_amount", 0) + 1


# Create your views here.
# the view for the page that takes you to the questions
def form(request):
    context_dict = {}
    #   this is fine for testing, but should be replaced by something more stable
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
    create_person_and_id(request)
    context_dict["log_amount"] = request.session.get("log_amount", 0)

    print("Person id is {id}".format(id=request.session["person"]))
    return render(request, "sleep_app/form.html", context_dict)


# the view for the page that asks about a specific symptom
def symptom_question(request, symptom_name_slug):
    context_dict = {}
    try:
        symptom = Symptom.objects.get(slug=symptom_name_slug)
        context_dict["symptom"] = symptom
        #       need to pass the proper type of response object to the template, depending on what type of response is needed
        if symptom.answer_type == "bool":
            response_form = YesNoResponseForm()
        elif symptom.answer_type == "text":
            response_form = TextResponseForm()
        else:
            response_form = ScaleResponseForm()
        context_dict["response_form"] = response_form
    except Symptom.DoesNotExist:
        context_dict["symptom"] = context_dict["response_form"] = None

    if request.method == "POST":
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
        #       for some reason we got here through a page with an invalid symptom slug. Should never happen.
        except Symptom.DoesNotExist:
            print(
                "ERROR: Symptom with slug {slug} does not exist.".format(
                    slug=symptom_name_slug
                )
            )
            return redirect("/form")

        try:
            current_person = Person.objects.get(id=request.session["person"])
            current_person.response.add(response)
            current_person.save()

        except Person.DoesNotExist:
            print("ERROR: Person with id {id} does not exist".format(id=request.session['person']))
            return redirect('/form')

        try:
            if (
                    symptom
                    == Symptom.objects.filter(symptom_type=symptom.symptom_type).last()
            ):
                increase_log_amount(request)
                return redirect('/location')
            else:
                next_symptom = next_in_order(symptom)
                return redirect("/form/{slug}".format(slug=next_symptom.slug))

        except Symptom.DoesNotExist:
            print("Symptom does not exist")
            return redirect("/form")

    return render(request, 'sleep_app/symptom_question.html', context=context_dict)


def location(request):
    if request.method == 'POST':
        try:
            current_person = Person.objects.get(id=request.session['person'])
            if request.POST["lat"] != "no-permission":
                current_person.lat = request.POST["lat"]
                current_person.long = request.POST["long"]
                current_person.save()
                print("ok lat " + current_person.lat + "long " + current_person.long)
# make sure that it is deleted *if and only if* no permission was given
            elif request.POST["lat"] == "no-permission":
                current_person.delete()
                print("no permission")
        except Person.DoesNotExist:
            print("ERROR: Person with id {id} does not exist".format(id=request.session['person']))
        return redirect('/form')

    return render(request, 'sleep_app/location.html')