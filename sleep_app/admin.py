from django.contrib import admin
from sleep_app.models import Person, Symptom, Response, YesNoResponse, TextResponse, ScaleResponse

# Register your models here.
admin.site.register(Person)
admin.site.register(YesNoResponse)
admin.site.register(TextResponse)
admin.site.register(ScaleResponse)
admin.site.register(Response)

class SymptomAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
# Update the registration to include this customised interface
admin.site.register(Symptom, SymptomAdmin)