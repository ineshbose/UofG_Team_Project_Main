from django.db import models
from django.template.defaultfilters import slugify
from polymorphic.models import PolymorphicModel
from datetime import datetime, date


class Symptom(models.Model):
    #   e.g. fever
    name = models.CharField(max_length=128)
    #   e.g. do you have a fever?
    question = models.CharField(max_length=256)

    #   the different types of answers that a question about a symptom could require
    ANSWER_TYPES = [("bool", "True/False"), ("int", "Scale"), ("text", "Text")]

    answer_type = models.CharField(max_length=4, choices=ANSWER_TYPES, default="bool")

    #   the "type" of the symptom, i.e. is this a symptom that a member of the public, a health care worker or a
    #   entomologist/vet will be able to log?
    SYMPTOM_TYPES = [
        ("MOP", "Member of public"),
        ("HCW", "Health care worker"),
        ("EOV", "Entomologist/vet"),
    ]

    symptom_type = models.CharField(max_length=4, choices=SYMPTOM_TYPES, default="MOP")

    #   the slug is used in the URL for the question about the symptom
    slug = models.SlugField(unique=True)

    #   optional picture
    image = models.ImageField(upload_to="symptoms", blank=True)

#   this is for django-next-prev. The symptoms are ordered by symptom_type and pk and can be iterated over in that
#   order in views. This makes it possible to display one symptom form per page, and to have a variable amount of
#   symptoms.
    class Meta:
        ordering = ("symptom_type", "pk")

    def save(self, *args, **kwargs):
        #if the symptom_type or answer_type is not is SYMPTOM_TYPES or ANSWER_TYPES then they get set to MOP or bool
        #should not usually happen
        #needs to be done in this slightly awkward way because django expects ANSWER_TYPES and SYMPTOM_TYPES to be of that
        #format
        if self.answer_type not in [a[0] for a in self.ANSWER_TYPES]:
            self.answer_type = 'bool'
        if self.symptom_type not in [s[0] for s in self.SYMPTOM_TYPES]:
            self.symptom_type = 'MOP'

        #       the name is concatenated with the symptom type because two symptoms of different types might have the same name

        self.slug = slugify(self.name + " " + self.symptom_type)
        super(Symptom, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


# The Person class needs a ManyToManyField(Response) to associate the responses a person made with that person.
# But there are different types of Responses (subclasses of Response). Making Response a PolymorphicModel ensures that
# when Person.response is accessed, we actually access instances of the subclasses of Response and not Response
# objects.
class Response(PolymorphicModel):
    pass


class Person(models.Model):
    id = models.IntegerField(primary_key=True)
    response = models.ManyToManyField(Response)

    date = models.DateTimeField(auto_now_add=True, blank=True)

#   this can be replaced by something more "fancy" (for example GeoDjango) once it is clear how the maps functionality
#   will be handled.
    lat = models.FloatField(null=True)
    long = models.FloatField(null=True)

    def save(self, *args, **kwargs):
        # both get set to None as soon as one is false, because a coordinate of, say,  "45, None" is of little use..
        if self.lat:
            if float(self.lat) < -90 or float(self.lat)> 90:
                self.lat = None
                self.long = None
        if self.long:
            if float(self.long) < -180 or float(self.long) > 180:
                self.lat = None
                self.long = None

        super(Person, self).save(*args, **kwargs)


class YesNoResponse(Response):
    answer = models.BooleanField(null=True)
    symptom = models.ForeignKey(Symptom, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "YesNoResponse: " + self.symptom.__str__()


class TextResponse(Response):
    # answer = models.CharField(max_length=1028, null=True)
    answer = models.TextField(max_length=2056, default="", blank=True)
    symptom = models.ForeignKey(Symptom, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "TextResponse: " + self.symptom.__str__()


class ScaleResponse(Response):
    answer = models.IntegerField(null=True)
    symptom = models.ForeignKey(Symptom, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "ScaleResponse: " + self.symptom.__str__()
