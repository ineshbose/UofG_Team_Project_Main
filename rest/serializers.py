from rest_framework import serializers
from sleep_app import models


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Person
        fields = "__all__"


class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Response
        fields = "__all__"


class SymptomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Symptom
        fields = "__all__"


class AnswerSetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.AnswerSet
        fields = "__all__"
