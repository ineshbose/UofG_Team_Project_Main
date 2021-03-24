from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

import plotly.graph_objs as go

from . import forms
from . import models


class SymptomModelTests(TestCase):
    def test_invalid_answer_type_set_to_bool(self):
        xyz_symptom = models.Symptom(
            name="xyz symptom", question="test?", answer_type="xyz", symptom_type="MOP"
        )
        xyz_symptom.save()
        # if it is a proper answer_type it won't get set to bool
        text_symptom = models.Symptom(
            name="text symptom",
            question="test?",
            answer_type="text",
            symptom_type="MOP",
        )
        text_symptom.save()
        self.assertEqual(xyz_symptom.answer_type, "bool")

        self.assertEqual(text_symptom.answer_type, "text")

    def test_invalid_symptom_type_set_to_MOP(self):
        xyz_symptom = models.Symptom(
            name="xyz symptom", question="test?", answer_type="bool", symptom_type="xyz"
        )
        xyz_symptom.save()
        # if it is a proper symptom_type it won't get set to hcw
        hcw_symptom = models.Symptom(
            name="hcw symptom", question="test?", answer_type="text", symptom_type="HCW"
        )
        hcw_symptom.save()

        self.assertEqual(xyz_symptom.symptom_type, "MOP")
        self.assertEqual(hcw_symptom.symptom_type, "HCW")

    def test_slug_is_name_and_symptom_type(self):
        xyz_symptom = models.Symptom(
            name="xyz symptom", question="test?", answer_type="bool", symptom_type="MOP"
        )
        xyz_symptom.save()
        self.assertEqual(xyz_symptom.slug, "xyz-symptom-mop")


class SymptomQuestionViewTests(TestCase):
    def test_symptom_does_not_exist(self):
        response = self.client.get(
            reverse(
                "sleep_app:symptom_form",
                kwargs={"symptom_name_slug": "fake-symptom-not-real"},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This symptom does not exist!")
        self.assertIsNone(response.context["symptom"])
        self.assertIsNone(response.context["response_form"])

    def test_proper_context_dict_for_existing_symptom(self):
        xyz_symptom = models.Symptom(
            name="xyz symptom", question="test?", answer_type="bool", symptom_type="MOP"
        )
        xyz_symptom.save()
        response_form = forms.YesNoResponseForm()
        response = self.client.get(
            reverse(
                "sleep_app:symptom_form", kwargs={"symptom_name_slug": xyz_symptom.slug}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["symptom"], xyz_symptom)
        #       the response_form placed in the context dict will not be the same object as the one created here, but it should
        #       have the same type
        self.assertEqual(type(response.context["response_form"]), type(response_form))

    def test_info_name_is_displayed(self):
        xyz_symptom = models.Symptom(
            name="xyz symptom",
            question="Is this a test question?",
            answer_type="bool",
            symptom_type="MOP",
        )
        xyz_symptom.save()
        response = self.client.get(
            reverse(
                "sleep_app:symptom_form", kwargs={"symptom_name_slug": xyz_symptom.slug}
            )
        )
        #       might want to add tests for answer_type later
        self.assertContains(response, "xyz symptom")
        self.assertContains(response, "Is this a test question?")

    def test_submit_redirects_to_next_symptom(self):
        first_symptom = models.Symptom(
            name="first symptom",
            question="Is this a test question?",
            answer_type="bool",
            symptom_type="MOP",
        )
        first_symptom.save()
        second_symptom = models.Symptom(
            name="second symptom",
            question="Is this a test question?",
            answer_type="bool",
            symptom_type="MOP",
        )
        second_symptom.save()

        current_person = models.Person(id=123)
        current_person.save()

        #       needs to be done like this -
        #       see https://docs.djangoproject.com/en/3.1/topics/testing/tools/#django.test.Client.session
        session = self.client.session
        session["person"] = current_person.id
        session.save()

        response = self.client.post(
            reverse(
                "sleep_app:symptom_form",
                kwargs={"symptom_name_slug": first_symptom.slug},
            )
        )

        self.assertRedirects(
            response,
            reverse(
                "sleep_app:symptom_form",
                kwargs={"symptom_name_slug": second_symptom.slug},
            ),
        )

    def test_last_symptom_redirects_to_location(self):
        with self.settings(
            STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
        ):
            xyz_symptom = models.Symptom(
                name="xyz symptom",
                question="Is this a test question?",
                answer_type="bool",
                symptom_type="MOP",
            )
            xyz_symptom.save()

            current_person = models.Person(id=123)
            current_person.save()

            session = self.client.session
            session["person"] = current_person.id
            session.save()

            response = self.client.post(
                reverse(
                    "sleep_app:symptom_form",
                    kwargs={"symptom_name_slug": xyz_symptom.slug},
                )
            )

            self.assertRedirects(response, reverse("sleep_app:location"))

    def test_yes_no_response_is_associated_with_person(self):
        xyz_symptom = models.Symptom(
            name="xyz symptom",
            question="Is this a test question?",
            answer_type="bool",
            symptom_type="MOP",
        )
        xyz_symptom.save()

        current_person = models.Person(id=456)
        current_person.save()

        session = self.client.session
        session["person"] = current_person.id
        session.save()

        self.client.post(
            reverse(
                "sleep_app:symptom_form", kwargs={"symptom_name_slug": xyz_symptom.slug}
            ),
            {"bool_response": True},
        )

        self.assertEqual(len(current_person.answerset_set.all()), 1)
        answer_set = current_person.answerset_set.all()[0]
        self.assertEqual(answer_set.response.bool_response, True)

    def test_text_response_is_associated_with_person(self):
        xyz_symptom = models.Symptom(
            name="xyz symptom",
            question="Is this a test question?",
            answer_type="text",
            symptom_type="MOP",
        )
        xyz_symptom.save()
        current_person = models.Person(id=456)
        current_person.save()

        session = self.client.session
        session["person"] = current_person.id
        session.save()

        self.client.post(
            reverse(
                "sleep_app:symptom_form", kwargs={"symptom_name_slug": xyz_symptom.slug}
            ),
            {"text_response": "This is what I want to say!"},
        )

        self.assertEqual(len(current_person.answerset_set.all()), 1)
        answer_set = current_person.answerset_set.all()[0]
        self.assertEqual(
            answer_set.response.text_response, "This is what I want to say!"
        )

    def test_scale_response_is_associated_with_person(self):
        xyz_symptom = models.Symptom(
            name="xyz symptom",
            question="Is this a test question?",
            answer_type="int",
            symptom_type="MOP",
        )
        xyz_symptom.save()
        current_person = models.Person(id=456)
        current_person.save()

        session = self.client.session
        session["person"] = current_person.id
        session.save()

        self.client.post(
            reverse(
                "sleep_app:symptom_form", kwargs={"symptom_name_slug": xyz_symptom.slug}
            ),
            {"scale_response": 2},
        )

        self.assertEqual(len(current_person.answerset_set.all()), 1)
        answer_set = current_person.answerset_set.all()[0]
        self.assertEqual(answer_set.response.scale_response, 2)

    def test_new_person_is_created_when_clicking_on_the_first_symptom(self):
        xyz_symptom = models.Symptom(
            name="xyz symptom",
            question="Is this a test question?",
            answer_type="int",
            symptom_type="MOP",
        )
        xyz_symptom.save()
        self.client.post(
            reverse(
                "sleep_app:symptom_form", kwargs={"symptom_name_slug": xyz_symptom.slug}
            ),
            {"first": ""},
        )
        self.assertEqual(models.Person.objects.all().count(), 1)

    def test_cancel_button_deletes_current_person(self):
        xyz_symptom = models.Symptom(
            name="xyz symptom",
            question="Is this a test question?",
            answer_type="int",
            symptom_type="MOP",
        )
        xyz_symptom.save()
        current_person = models.Person(id=456)
        current_person.save()

        session = self.client.session
        session["person"] = current_person.id
        session.save()
        self.client.post(reverse("sleep_app:main_form_page"), {"cancel": ""})
        self.assertIsNone(session.get("Person"))
        self.assertEqual(models.Person.objects.all().count(), 0)


class LocationViewTests(TestCase):
    def test_coordinates_are_saved_if_permission_is_given(self):
        with self.settings(
            STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
        ):

            # lat:49.748235, long: 6.658348
            current_person = models.Person(id=456)
            current_person.save()

            session = self.client.session
            session["person"] = current_person.id
            session.save()

            self.client.post(
                reverse("sleep_app:location"), {"lat": "49.748235", "long": "6.658348"}
            )

            #       need to get the object from the database again to access the latest changes
            current_person = models.Person.objects.get(id=456)
            self.assertEqual(current_person.gps_location, "49.748235,6.658348")


class TableTest(TestCase):
    def test_bool_data_is_added_to_table(self):
        user = User(username="test", password="123")
        user.is_staff = True
        user.save()
        self.client.force_login(user)
        person = models.Person(id=123)
        person.save()
        xyz_symptom = models.Symptom(
            name="xyz symptom",
            question="Do you have xyz?",
            answer_type="bool",
            symptom_type="MOP",
        )

        xyz_symptom.save()
        xyz_response = models.Response(symptom=xyz_symptom, bool_response=True)
        xyz_response.save()
        answer_set = models.AnswerSet(person=person, response=xyz_response)
        answer_set.save()
        response = self.client.get(reverse("sleep_app:table"))
        self.assertContains(
            response,
            "<th>xyz symptom</th>",
            html=True,
        )
        self.assertContains(response, "<td>True</td>", html=True)

    def test_text_data_is_added_to_table(self):
        user = User(username="test", password="123")
        user.is_staff = True
        user.save()
        self.client.force_login(user)
        person = models.Person(id=123)
        person.save()
        abc_symptom = models.Symptom(
            name="abc symptom",
            question="What is your abc?",
            answer_type="text",
            symptom_type="MOP",
        )

        abc_symptom.save()
        abc_response = models.Response(
            symptom=abc_symptom, text_response="My abc is asdfsd"
        )
        abc_response.save()
        answer_set = models.AnswerSet(person=person, response=abc_response)
        answer_set.save()
        response = self.client.get(reverse("sleep_app:table"))
        self.assertContains(
            response,
            "<th>abc symptom</th>",
            html=True,
        )
        self.assertContains(response, "<td>My abc is asdfsd</td>", html=True)

    def test_scale_data_is_added_to_table(self):
        user = User(username="test", password="123")
        user.is_staff = True
        user.save()
        self.client.force_login(user)
        person = models.Person(id=123)
        person.save()
        cde_symptom = models.Symptom(
            name="abc symptom",
            question="How much abc do you have?",
            answer_type="int",
            symptom_type="MOP",
        )
        cde_symptom.save()
        cde_response = models.Response(symptom=cde_symptom, scale_response=4)
        cde_response.save()
        answer_set = models.AnswerSet(person=person, response=cde_response)
        answer_set.save()
        response = self.client.get(reverse("sleep_app:table"))
        self.assertContains(
            response,
            "<th>abc symptom</th>",
            html=True,
        )
        self.assertContains(response, "<td>4</td>", html=True)


class MapTest(TestCase):
    def test_person_data_is_added_to_map(self):
        user = User(username="test", password="123")
        user.is_staff = True
        user.save()
        self.client.force_login(user)

        current_person = models.Person(id=123)
        current_person.gps_location = "50,50"
        current_person.save()

        session = self.client.session
        session["person"] = current_person.id
        session.save()

        response = self.client.get(reverse("sleep_app:map"))
        latitude = ["50"]
        longitude = ["50"]
        id = [123]

        fig = go.Figure(
            data=go.Scattergeo(
                lon=latitude,
                lat=longitude,
                text=id,
                mode="markers",
                marker=dict(
                    color="red",
                    opacity=0.8,
                    symbol="circle",
                    line=dict(width=1, color="rgba(102, 102, 102)"),
                    cmin=0,
                    size=5,
                    cmax=5,
                ),
            )
        )

        self.assertEqual(response.context["figure"].data[0], fig.data[0])


class RegisterTest(TestCase):
    def test_user_is_added_if_successful(self):
        self.client.post(
            reverse("sleep_app:register"),
            {
                "username": "test",
                "email": "test@testmail.com",
                "password1": "myVerySecurePassworddsagretgahwrt4235132454231r5",
                "password2": "myVerySecurePassworddsagretgahwrt4235132454231r5",
            },
        )
        self.assertEqual(User.objects.filter(username="test").count(), 1)

    def test_failure_if_password_is_common(self):
        response = self.client.post(
            reverse("sleep_app:register"),
            {
                "username": "test",
                "email": "test@testmail.com",
                "password1": "password",
                "password2": "password",
            },
        )

        self.assertContains(response, "This password is too common.", html=True)

    def test_failure_if_user_exists(self):
        testuser = User(
            username="test", email="test@test.com", password="rfdgadfgearger"
        )
        testuser.save()

        response = self.client.post(
            reverse("sleep_app:register"),
            {
                "username": "test",
                "email": "test@test.com",
                "password1": "rtgqergehwty5jhw5yhr",
                "password2": "rtgqergehwty5jhw5yhr",
            },
        )

        self.assertContains(
            response, "A user with that username already exists.", html=True
        )
