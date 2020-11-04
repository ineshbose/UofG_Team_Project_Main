from django import forms
from sleep_app.models import Person, Symptom, YesNoResponse, TextResponse, ScaleResponse


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
