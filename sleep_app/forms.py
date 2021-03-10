from django import forms
from . import models
from django.contrib.auth.forms import UserCreationForm, User


class YesNoResponseForm(forms.ModelForm):
    bool_response = forms.BooleanField(widget=forms.NullBooleanSelect, required=False)

    class Meta:
        model = models.Response
        fields = ("bool_response",)


class TextResponseForm(forms.ModelForm):
    text_response = forms.TextInput()

    class Meta:
        model = models.Response
        fields = ("text_response",)


class ScaleResponseForm(forms.ModelForm):
    scale_response = forms.IntegerField()

    class Meta:
        model = models.Response
        fields = ("scale_response",)


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
