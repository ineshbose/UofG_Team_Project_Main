from django.urls import path
from sleep_app import views

app_name = 'sleep_app'


urlpatterns = [
    path('form/<slug:symptom_name_slug>/',
         views.symptom_question, name='symptom form'),
    path('form/', views.form, name='main form page'),
    path('map/',views.map, name='map'),
]
