from django.contrib import admin
from django.urls import path
from django.urls import include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers
from rest import views as rest_views


router = routers.DefaultRouter()
router.register(r"persons", rest_views.PersonViewSet)
router.register(r"responses", rest_views.ResponseViewSet)
router.register(r"symptoms", rest_views.SymptomViewSet)
router.register(r"answersets", rest_views.AnswerSetViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("sleep_app.urls")),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    # path('django_plotly_dash/', include('django_plotly_dash.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
