from django.urls import path
from sleep_app import views

app_name = 'sleep_app'


urlpatterns = [
    path('form/<slug:symptom_name_slug>/',
         views.symptom_question, name='symptom_form'),
    path('form/', views.form, name='main_form_page'),
    path('location/', views.location, name='location')
]
