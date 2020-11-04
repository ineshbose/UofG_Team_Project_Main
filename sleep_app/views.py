from django.shortcuts import render
from sleep_app.models import Symptom, Person, Response, YesNoResponse, TextResponse, ScaleResponse
from sleep_app.forms import YesNoResponseForm, TextResponseForm, ScaleResponseForm
import random
import datetime
from django.shortcuts import redirect

from next_prev import next_in_order, prev_in_order
from django.http import HttpResponse

def map(request):
    context_dict = {}

    return render(request,'sleep_app/map.html', context_dict)

# helper function. Generates a person object with a unique random id whenever the first page of a question is visited.
def create_person_and_id(request):
    new_id = int(random.uniform(0, 1000000))
#   to prevent id collision
    while request.session.get('person') == new_id:
        new_id = int(random.uniform(0, 1000000))
    person = Person(id=new_id)
    person.save()
    request.session['person'] = person.id


def increase_log_amount(request):
    request.session['log_amount'] = request.session.get('log_amount', 0) + 1


# Create your views here.
# the view for the page that takes you to the questions
def form(request):
    context_dict = {}
#   this is fine for testing, but should be replaced by something more stable
    first_symptom_mop = Symptom.objects.filter(symptom_type='MOP').first()
    first_symptom_hcw = Symptom.objects.filter(symptom_type='HCW').first()
    first_symptom_eov = Symptom.objects.filter(symptom_type='EOV').first()
    context_dict = {'first_symptom_mop':first_symptom_mop,
                    'first_symptom_hcw':first_symptom_hcw,
                    'first_symptom_eov':first_symptom_eov}

#   this means that that the session will expire in *24h*, not at the beginning of the next day
#   1209600 is the default return value
#   (https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-SESSION_COOKIE_AGE)
    if request.session.get_expiry_age() == 1209600:
        request.session.set_expiry(60*60*24)
    create_person_and_id(request)
    context_dict['log_amount'] = request.session.get('log_amount', 0)

    print("Person id is {id}".format(id = request.session['person']))
    return render(request, 'sleep_app/form.html', context_dict)


# the view for the page that asks about a specific symptom
def symptom_question(request, symptom_name_slug):
    context_dict = {}
    try:
        symptom = Symptom.objects.get(slug=symptom_name_slug)
        context_dict['symptom'] = symptom
#       need to pass the proper type of response object to the template, depending on what type of response is needed
        if symptom.answer_type == 'bool':
            response_form = YesNoResponseForm()
        elif symptom.answer_type == 'text':
            response_form = TextResponseForm()
        else:
            response_form = ScaleResponseForm()
        context_dict['response_form'] = response_form
    except Symptom.DoesNotExist:
        context_dict['symptom'] = context_dict['response_form'] = None

    if request.method == 'POST':
        try:
            symptom = Symptom.objects.get(slug=symptom_name_slug)
            if symptom.answer_type == 'bool':
                response_form = YesNoResponseForm(request.POST)
                if response_form.is_valid():
                    response = YesNoResponse(symptom=symptom, answer=response_form.cleaned_data['answer'])
                    response.save()
            elif symptom.answer_type == 'text':
                response_form = TextResponseForm(request.POST)
                if response_form.is_valid():
                    response = TextResponse(symptom=symptom, answer=response_form.cleaned_data['answer'])
                    response.save()
            else:
                response_form = ScaleResponseForm(request.POST)
                if response_form.is_valid():
                    response = ScaleResponse(symptom=symptom, answer=response_form.cleaned_data['answer'])
                    response.save()
#       for some reason we got here through a page with an invalid symptom slug. Should never happen.
        except Symptom.DoesNotExist:
            print("ERROR: Symptom with slug {slug} does not exist.".format(slug=symptom_name_slug))
            return redirect('/form')

        try:
            current_person = Person.objects.get(id=request.session['person'])
            current_person.response.add(response)
            current_person.save()

        except Person.DoesNotExist:
            print("ERROR: Person with id {id} does not exist".format(id=request.session['person']))
            return redirect('/form')

#       this is probably NOT a good way of getting to the next symptom!
        try:
            if symptom == Symptom.objects.filter(symptom_type=symptom.symptom_type).last():
                increase_log_amount(request)
                return redirect('/form')
            else:
                # next_symptom = None
                # key = symptom.pk
                # while not next_symptom:
                #     key = key + 1
                #     next_symptom = Symptom.objects.filter(pk=key).first()
                next_symptom = next_in_order(symptom)
                return redirect('/form/{slug}'.format(slug=next_symptom.slug))

        except Symptom.DoesNotExist:
            print("Symptom does not exist")
            return redirect('/form')

    return render(request, 'sleep_app/symptom_question.html', context=context_dict)