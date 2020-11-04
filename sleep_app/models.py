from django.db import models
from django.template.defaultfilters import slugify
from polymorphic.models import PolymorphicModel


class Symptom(models.Model):
#   e.g. fever
    name = models.CharField(max_length=128)
#   e.g. do you have a fever?
    question = models.CharField(max_length=256)

#   the different types of answers that a question about a symptom could require
    ANSWER_TYPES = [('bool', 'True/False'),
                   ('int', 'Scale'),
                    ('text', 'Text')]

    answer_type = models.CharField(max_length=4, choices=ANSWER_TYPES, default='bool')

#   the "type" of the symptom, i.e. is this a symptom that a member of the public, a health care worker or a
#   entomologist/vet will be able to log?
    SYMPTOM_TYPES = [('MOP', 'Member of public'),
                     ('HCW', 'Health care worker'),
                     ('EOV', 'Entomologist/vet')]

    symptom_type = models.CharField(max_length=4, choices=SYMPTOM_TYPES, default='MOP')


#   the slug is used in the URL for the question about the symptom
    slug = models.SlugField(unique=True)

#   optional picture
    image = models.ImageField(upload_to='symptoms', blank=True)

#   this is form django-next-prev. The symptoms are ordered by symptom_type and pk and can be iterated over in that
#   order in views. This makes it possible to display one symptom form per page, and to have a variable amount of
#   symptoms.
    class Meta:
        ordering = ('symptom_type', 'pk')

    def save(self, *args, **kwargs):
#       the name is concatenated with the symptom type because two symptoms of different types might have the same name
        self.slug = slugify(self.name+ " " + self.symptom_type)
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


class YesNoResponse(Response):
    answer = models.BooleanField(null=True)
    symptom = models.ForeignKey(Symptom, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "YesNoResponse: " + self.symptom.__str__()


class TextResponse(Response):
    #answer = models.CharField(max_length=1028, null=True)
    answer = models.TextField(max_length=2056, default="", blank=True)
    symptom = models.ForeignKey(Symptom, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "TextResponse: " + self.symptom.__str__()


class ScaleResponse(Response):
    answer = models.IntegerField(null=True)
    symptom = models.ForeignKey(Symptom, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "ScaleResponse: " + self.symptom.__str__()



