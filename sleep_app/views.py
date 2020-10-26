from django.shortcuts import render
from sleep_app.models import Symptom, Person, Response, YesNoResponse, TextResponse, ScaleResponse
from sleep_app.forms import YesNoResponseForm, TextResponseForm, ScaleResponseForm
from django.shortcuts import redirect
from django.http import HttpResponse
# Create your views here.



def map(request):
    context_dict = {}

    return render(request,'sleep_app/map.html', context_dict)

#the view for the page that takes you to the questions
def form(request):
    context_dict = {}
#   this is fine for testing, but should be replaced by something more stable
    first_symptom = Symptom.objects.get(pk=1)
    context_dict['first_symptom'] = first_symptom
#   set a cookie, so that all responses can be associated with one person
#   this is fine for testing, but should be replaced by something more stable
    if 'person' not in request.session.keys():
        person = Person()
        person.save()
        request.session['person'] = person.pk
    return render(request, 'sleep_app/form.html', context_dict)


#the view for the page that asks about a specific symptom
def symptom_question(request, symptom_name_slug):
    context_dict = {}
    try:
        symptom = Symptom.objects.get(slug=symptom_name_slug)
        context_dict['symptom'] = symptom
#       need to pass the proper type of response object to the template, depending on what type of response is needed
        if symptom.answer_type == 'bool':
            response = YesNoResponse(symptom=symptom)
            context_dict['response'] = response
            response_form = YesNoResponseForm()
        elif symptom.answer_type == 'text':
            response = TextResponse(symptom=symptom)
            context_dict['response'] = response
            response_form = TextResponseForm()
        else:
            response = ScaleResponse(symptom=symptom)
            context_dict['response'] = response
            response_form = ScaleResponseForm()
        context_dict['response_form'] = response_form
    except Symptom.DoesNotExist:
        context_dict['symptom'] = context_dict['response'] = context_dict['response_form'] = None

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
#       for some reason we got here through a page with an invalid symptom slug. Should never happen
        except Symptom.DoesNotExist:
            return redirect('/form')

        try:
            current_person = Person.objects.get(pk=request.session['person'])
            current_person.response.add(response)
            current_person.save()
        except Person.DoesNotExist:
            return redirect('/form')

#       this is probably NOT a good way of getting to the next symptom!
        try:
            next_symptom = Symptom.objects.get(pk=symptom.pk + 1)
            return redirect('/form/{slug}'.format(slug=next_symptom.slug))

        except Symptom.DoesNotExist:
            context_dict['symptom'] = context_dict['response'] = context_dict['response_form'] = None
            return redirect('/form')

    return render(request, 'sleep_app/symptom_question.html', context=context_dict)