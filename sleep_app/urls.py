from django.urls import path
from sleep_app import views

app_name = 'sleep_app'


urlpatterns = [
    path('', views.index, name='index'),
    path('form/<slug:symptom_name_slug>/',
         views.symptom_question, name='symptom_form'),
    path('form/', views.form, name='main_form_page'),
    path('map/',views.map, name='map'),
]
