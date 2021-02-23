from django import forms
from sleep_app.models import Person, Symptom, Response
from django.contrib.auth.forms import UserCreationForm, User


class YesNoResponseForm(forms.ModelForm):
    #   needs to be required=False because the answer can be yes or no
    bool_response = forms.BooleanField(widget=forms.NullBooleanSelect, required=False)

    class Meta:
        model = Response
        fields = ("bool_response",)


class TextResponseForm(forms.ModelForm):
    text_response = forms.TextInput()

    class Meta:
        model = Response
        fields = ("text_response",)


class ScaleResponseForm(forms.ModelForm):
    scale_response = forms.IntegerField()

    class Meta:
        model = Response
        fields = ("scale_response",)


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
