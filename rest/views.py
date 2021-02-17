from django.shortcuts import render
from sleep_app import models
from . import serializers
from rest_framework import viewsets, permissions

# Create your views here.
class PersonViewSet(viewsets.ModelViewSet):
    queryset = models.Person.objects.all()
    serializer_class = serializers.PersonSerializer
    permission_classes = [permissions.IsAuthenticated]


class ResponseViewSet(viewsets.ModelViewSet):
    queryset = models.Response.objects.all()
    serializer_class = serializers.ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]


class SymptomViewSet(viewsets.ModelViewSet):
    queryset = models.Symptom.objects.all()
    serializer_class = serializers.SymptomSerializer
    permission_classes = [permissions.IsAuthenticated]
