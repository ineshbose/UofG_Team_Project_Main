from django.contrib import admin
from . import models


class SymptomAdmin(admin.ModelAdmin):
    model = models.Symptom
    prepopulated_fields = {"slug": ("name",)}


class AnswerSetInline(admin.TabularInline):
    model = models.AnswerSet
    fk_name = "person"
    extra = 0

class PersonAdmin(admin.ModelAdmin):
    model = models.Person
    inlines = [
        AnswerSetInline,
    ]

#admin.site.register(models.Person)
admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.Response)
#admin.site.register(models.AnswerSet, AnswerSetInline)
admin.site.register(models.Symptom, SymptomAdmin)
