from django.test import TestCase
from sleep_app.models import Symptom, Person

from django.test import TestCase
from sleep_app.models import Symptom, Person, Response, YesNoResponse, ScaleResponse, TextResponse
from sleep_app.forms import YesNoResponseForm
from django.urls import reverse


# Create your tests here.
class SymptomModelTests(TestCase):
    def test_invalid_answer_type_set_to_bool(self):
        xyz_symptom = Symptom(name="xyz symptom", question="test?", answer_type='xyz',
                              symptom_type='MOP')
        xyz_symptom.save()
        # if it is a proper answer_type it won't get set to bool
        text_symptom = Symptom(name="text symptom", question="test?", answer_type='text',
                               symptom_type='MOP')
        text_symptom.save()
        self.assertEqual(xyz_symptom.answer_type,'bool')

        self.assertEqual(text_symptom.answer_type, 'text')

    def test_invalid_symptom_type_set_to_MOP(self):
        xyz_symptom = Symptom(name="xyz symptom", question="test?", answer_type='bool',
                              symptom_type='xyz')
        xyz_symptom.save()
        # if it is a proper symptom_type it won't get set to hcw
        hcw_symptom = Symptom(name="hcw symptom", question="test?", answer_type='text',
                              symptom_type='HCW')
        hcw_symptom.save()

        self.assertEqual(xyz_symptom.symptom_type,'MOP')
        self.assertEqual(hcw_symptom.symptom_type, 'HCW')

    def test_slug_is_name_and_symptom_type(self):
        xyz_symptom = Symptom(name="xyz symptom", question="test?", answer_type='bool',
                              symptom_type='MOP')
        xyz_symptom.save()
        self.assertEqual(xyz_symptom.slug, "xyz-symptom-mop")


class PersonModelTests(TestCase):
    def test_invalid_coordinates_get_set_to_none(self):
        person_lat_small = Person(id=1, lat=-91, long=100)
        person_lat_small.save()
        person_lat_big = Person(id=2, lat=91, long=100)
        person_lat_big.save()
        person_long_small = Person(id=3, lat=80, long=-181)
        person_long_small.save()
        person_long_big = Person(id=4, lat=80, long=181)
        person_long_big.save()
        self.assertIsNone(person_lat_small.lat)
        self.assertIsNone(person_lat_big.lat)
        self.assertIsNone(person_long_small.long)
        self.assertIsNone(person_long_big.long)


class SymptomQuestionViewTests(TestCase):
    def test_symptom_does_not_exist(self):
        response = self.client.get(reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                                 'fake-symptom-not-real'}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This symptom does not exist!")
        self.assertIsNone(response.context["symptom"])
        self.assertIsNone(response.context["response_form"])

    def test_proper_context_dict_for_existing_symptom(self):
        xyz_symptom = Symptom(name="xyz symptom", question="test?", answer_type='bool',
                              symptom_type='MOP')
        xyz_symptom.save()
        response_form = YesNoResponseForm()
        response = self.client.get(reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                                 xyz_symptom.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["symptom"], xyz_symptom)
        #       the response_form placed in the context dict will not be the same object as the one created here, but it should
        #       have the same type
        self.assertEqual(type(response.context["response_form"]), type(response_form))

    def test_info_name_is_displayed(self):
        xyz_symptom = Symptom(name="xyz symptom", question="Is this a test question?", answer_type='bool',
                              symptom_type='MOP')
        xyz_symptom.save()
        response = self.client.get(reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                                 xyz_symptom.slug}))
        #       might want to add tests for answer_type later
        self.assertContains(response, "xyz symptom")
        self.assertContains(response, "Is this a test question?")

    def test_submit_redirects_to_next_symptom(self):
        first_symptom = Symptom(name="first symptom", question="Is this a test question?", answer_type='bool',
                                symptom_type='MOP')
        first_symptom.save()
        second_symptom = Symptom(name="second symptom", question="Is this a test question?", answer_type='bool',
                                 symptom_type='MOP')
        second_symptom.save()

        current_person = Person(id=123)
        current_person.save()

        #       needs to be done like this -
        #       see https://docs.djangoproject.com/en/3.1/topics/testing/tools/#django.test.Client.session
        session = self.client.session
        session["person"] = current_person.id
        session.save()

        response = self.client.post(reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                                  first_symptom.slug}))

        self.assertRedirects(response, reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                                     second_symptom.slug}))

    def test_last_symptom_redirects_to_location(self):
        xyz_symptom = Symptom(name="xyz symptom", question="Is this a test question?", answer_type='bool',
                              symptom_type='MOP')
        xyz_symptom.save()

        current_person = Person(id=123)
        current_person.save()

        session = self.client.session
        session["person"] = current_person.id
        session.save()

        response = self.client.post(reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                                  xyz_symptom.slug}))

        self.assertRedirects(response, reverse('sleep_app:location'))

    def test_yes_no_response_is_associated_with_person(self):
        xyz_symptom = Symptom(name="xyz symptom", question="Is this a test question?", answer_type='bool',
                              symptom_type='MOP')
        xyz_symptom.save()

        current_person = Person(id=456)
        current_person.save()

        session = self.client.session
        session["person"] = current_person.id
        session.save()

        self.client.post(reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                    xyz_symptom.slug}),
                         {"answer": True})

        self.assertEqual(len(current_person.response.all()), 1)
        response = current_person.response.all()[0]
        self.assertEqual(response.answer, True)

    def test_text_response_is_associated_with_person(self):
        xyz_symptom = Symptom(name="xyz symptom", question="Is this a test question?", answer_type='text',
                              symptom_type='MOP')
        xyz_symptom.save()
        current_person = Person(id=456)
        current_person.save()

        session = self.client.session
        session["person"] = current_person.id
        session.save()

        self.client.post(reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                    xyz_symptom.slug}),
                         {"answer": "This is what I want to say!"})

        self.assertEqual(len(current_person.response.all()), 1)
        response = current_person.response.all()[0]
        self.assertEqual(response.answer, "This is what I want to say!")

    def test_scale_response_is_associated_with_person(self):
        xyz_symptom = Symptom(name="xyz symptom", question="Is this a test question?", answer_type='int',
                              symptom_type='MOP')
        xyz_symptom.save()
        current_person = Person(id=456)
        current_person.save()

        session = self.client.session
        session["person"] = current_person.id
        session.save()

        self.client.post(reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                    xyz_symptom.slug}),
                         {"answer": 2})

        self.assertEqual(len(current_person.response.all()), 1)
        response = current_person.response.all()[0]
        self.assertEqual(response.answer, 2)

    def test_new_person_is_created_when_clicking_on_the_first_symptom(self):
        xyz_symptom = Symptom(name="xyz symptom", question="Is this a test question?", answer_type='int',
                              symptom_type='MOP')
        xyz_symptom.save()
        self.client.post(reverse('sleep_app:symptom_form', kwargs={'symptom_name_slug':
                                                                   xyz_symptom.slug}), {"first":""})
        self.assertEqual(Person.objects.all().count(), 1)

    def test_cancel_button_deletes_current_person(self):
        xyz_symptom = Symptom(name="xyz symptom", question="Is this a test question?", answer_type='int',
                              symptom_type='MOP')
        xyz_symptom.save()
        current_person = Person(id=456)
        current_person.save()

        session = self.client.session
        session["person"] = current_person.id
        session.save()
        self.client.post(reverse('sleep_app:main_form_page'), {"cancel": ""})
        self.assertIsNone(session.get("Person"))
        self.assertEqual(Person.objects.all().count(), 0)


class LocationViewTests(TestCase):
    def test_coordinates_are_saved_if_permission_is_given(self):
        # lat:49.748235, long: 6.658348
        current_person = Person(id=456)
        current_person.save()

        session = self.client.session
        session["person"] = current_person.id
        session.save()

        self.client.post(reverse('sleep_app:location'), {'lat': "49.748235", 'long': "6.658348"})

#       need to get the object from the database again to access the latest changes
        current_person = Person.objects.get(id=456)
        self.assertEqual(current_person.lat, 49.748235)
        self.assertEqual(current_person.long, 6.658348)


class TableTest(TestCase):
    def test_bool_data_is_added_to_table(self):
        person = Person(id=123)
        person.save()
        xyz_symptom = Symptom(name="xyz symptom", question="Do you have xyz?", answer_type='bool',
                              symptom_type='MOP')

        xyz_symptom.save()
        xyz_response = YesNoResponse(symptom=xyz_symptom, answer=True)
        xyz_response.save()
        person.response.add(xyz_response)
        response = self.client.get(reverse('sleep_app:table'))
        self.assertContains(response, """<th class="orderable">
                                        <a href="?sort=xyz+symptom">Xyz symptom</a>
                                        </th>""", html=True)
        self.assertContains(response, """<td >True</td>""", html=True)

    def test_text_data_is_added_to_table(self):
        person = Person(id=123)
        person.save()
        abc_symptom = Symptom(name="abc symptom", question="What is your abc?", answer_type='text',
                              symptom_type='MOP')

        abc_symptom.save()
        abc_response = TextResponse(symptom=abc_symptom, answer="My abc is asdfsd")
        abc_response.save()
        person.response.add(abc_response)
        response = self.client.get(reverse('sleep_app:table'))
        self.assertContains(response, """<th class="orderable">
                                        <a href="?sort=abc+symptom">Abc symptom</a>
                                        </th>""", html=True)
        self.assertContains(response, """<td >My abc is asdfsd</td>""", html=True)

    def test_scale_data_is_added_to_table(self):
        person = Person(id=123)
        person.save()
        abc_symptom = Symptom(name="abc symptom", question="How much abc do you have?", answer_type='scale',
                              symptom_type='MOP')

        abc_symptom.save()
        abc_response = ScaleResponse(symptom=abc_symptom, answer=4)
        abc_response.save()
        person.response.add(abc_response)
        response = self.client.get(reverse('sleep_app:table'))
        self.assertContains(response, """<th class="orderable">
                                        <a href="?sort=abc+symptom">Abc symptom</a>
                                        </th>""", html=True)
        self.assertContains(response, """<td >4</td>""", html=True)
