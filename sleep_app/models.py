from django.db import models
from django.template.defaultfilters import slugify
from location_field.models.plain import PlainLocationField


class Symptom(models.Model):
    name = models.CharField(max_length=128)
    question = models.CharField(max_length=256)

    ANSWER_TYPES = [
        ("int", "Scale"),
        ("text", "Text"),
        ("bool", "True/False"),
    ]

    answer_type = models.CharField(max_length=4, choices=ANSWER_TYPES, default="bool")

    SYMPTOM_TYPES = [
        ("MOP", "Member of public"),
        ("HCW", "Health care worker"),
        ("EOV", "Entomologist/vet"),
    ]

    symptom_type = models.CharField(max_length=4, choices=SYMPTOM_TYPES, default="MOP")

    slug = models.SlugField(unique=True)

    image = models.ImageField(upload_to="symptoms", blank=True)

    class Meta:
        ordering = ("symptom_type", "pk")

    def save(self, *args, **kwargs):
        if self.answer_type not in [a[0] for a in self.ANSWER_TYPES]:
            self.answer_type = "bool"
        if self.symptom_type not in [s[0] for s in self.SYMPTOM_TYPES]:
            self.symptom_type = "MOP"

        self.slug = slugify(self.name + " " + self.symptom_type)
        super(Symptom, self).save(*args, **kwargs)

    def __str__(self):
        return self.name + " - " + self.symptom_type


class Response(models.Model):
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    text_response = models.TextField(max_length=2056, blank=True, null=True)
    scale_response = models.IntegerField(null=True)
    bool_response = models.BooleanField(null=True)

    def __str__(self):
        choice_mapping = {
            "int": self.scale_response,
            "text": self.text_response,
            "bool": self.bool_response,
        }
        return (
            f'{self.symptom}: {choice_mapping.get(self.symptom.answer_type, "<error>")}'
        )


class Person(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    gps_location = PlainLocationField(based_fields=["city"], zoom=7, null=True)
    db_location = PlainLocationField(based_fields=["city"], zoom=7, null=True)
    location_text = models.CharField(max_length=256, blank=True, null=True)


class AnswerSet(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
