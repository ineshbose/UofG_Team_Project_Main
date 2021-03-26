from django.contrib import admin
from . import models


class SymptomAdmin(admin.ModelAdmin):
    model = models.Symptom
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("id", "name", "answer_type", "symptom_type")


class AnswerSetInline(admin.TabularInline):
    model = models.AnswerSet
    fk_name = "person"
    extra = 0


class PersonAdmin(admin.ModelAdmin):
    model = models.Person
    inlines = [
        AnswerSetInline,
    ]
    list_display = ("id", "date", "gps_location", "db_location", "location_text")


admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.Response)
admin.site.register(models.Symptom, SymptomAdmin)
