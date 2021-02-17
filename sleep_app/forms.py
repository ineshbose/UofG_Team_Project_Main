from django import forms
from sleep_app.models import Person, Symptom, YesNoResponse, TextResponse, ScaleResponse
from django.contrib.auth.forms import UserCreationForm, User


class YesNoResponseForm(forms.ModelForm):
    #   needs to be required=False because the answer can be yes or no
    answer = forms.BooleanField(widget=forms.NullBooleanSelect, required=False)

    class Meta:
        model = YesNoResponse
        fields = ("answer",)


class TextResponseForm(forms.ModelForm):
    answer = forms.TextInput()

    class Meta:
        model = TextResponse
        fields = ("answer",)


class ScaleResponseForm(forms.ModelForm):
    answer = forms.IntegerField()

    class Meta:
        model = ScaleResponse
        fields = ("answer",)


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
