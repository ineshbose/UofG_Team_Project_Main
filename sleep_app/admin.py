from django.contrib import admin
from . import models


class SymptomAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(models.Person)
admin.site.register(models.Response)
admin.site.register(models.Symptom, SymptomAdmin)
