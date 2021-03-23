import django_tables2 as tables

from . import models

# The table should have a row for each person, and columns "id", "date" "lat", "long" and then one column per symptom. A person's
# answer to a symptom question should be shown in the appropriate symptom column. django-tables2 does not offer a straight-forward
# way of doing this. The module is based on generating columns from the *fields* of a model, and not the *instances* of a
# model. The workaround here is to override __init__ and add a new column per symptom there. This cannot be done in the
# main class because (I assume) it is not possible to modify self.base_columns there. This is not how django-tables2 is
# supposed to be used, but there does not seem to be a better solution.


class PersonTable(tables.Table):

    id = tables.Column(verbose_name="Person ID")
    date = tables.Column(verbose_name="Date")
    location_text = tables.Column(verbose_name="Location")
    db_location = tables.Column(verbose_name="Map Database Coordinates")
    gps_location = tables.Column(verbose_name="GPS Coordinates")

    class Meta:
        template_name = "django_tables2/bootstrap.html"

    # https://stackoverflow.com/questions/39472441/django-tables2-add-dynamic-columns-to-table-class-from-hstore
    def __init__(self, data, *args, **kwargs):
        if data:
            symptoms = models.Symptom.objects.all()
            for s in symptoms:
                self.base_columns[str(s)] = tables.Column()
        super(PersonTable, self).__init__(data, *args, **kwargs)
