from django.urls import path
from sleep_app import views

# from sleep_app.views import TableListView

app_name = "sleep_app"


urlpatterns = [
    path("", views.index, name="index"),
    path("form/<slug:symptom_name_slug>/", views.symptom_question, name="symptom_form"),
    path("form/", views.form, name="main_form_page"),
    path("map/", views.map, name="map"),
    path("location/", views.location, name="location"),
    path("table/", views.table, name="table"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("success/", views.success, name="success"),
    path("export/", views.export_csv, name="export"),
]
