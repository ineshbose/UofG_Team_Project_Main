from django.test import TestCase
from sleep_app.models import Symptom, Person


# Create your tests here.
class SymptomModelTests(TestCase):
    def test_invalid_answer_type_set_to_bool(self):
        xyz_symptom = Symptom(name="xyz symptom", question="test?", answer_type='xyz',
                           symptom_type='MOP')
        xyz_symptom.save()
        #if it is a proper answer_type it won't get set to bool
        text_symptom = Symptom(name="text symptom", question="test?", answer_type='text',
                           symptom_type='MOP')
        text_symptom.save()
        self.assertEqual(xyz_symptom.answer_type,'bool')
        self.assertEqual(text_symptom.answer_type, 'text')

    def test_invalid_symptom_type_set_to_MOP(self):
        xyz_symptom = Symptom(name="xyz symptom", question="test?", answer_type='bool',
                           symptom_type='xyz')
        xyz_symptom.save()
        #if it is a proper symptom_type it won't get set to hcw
        hcw_symptom = Symptom(name="hcw symptom", question="test?", answer_type='text',
                           symptom_type='HCW')
        hcw_symptom.save()
        self.assertEqual(xyz_symptom.symptom_type,'MOP')
        self.assertEqual(hcw_symptom.symptom_type, 'HCW')

    def test_slug_is_name_and_symptom_type(self):
        xyz_symptom = Symptom(name="xyz symptom", question="test?", answer_type='bool',
                              symptom_type='MOP')
        xyz_symptom.save()
        self.assertEqual(xyz_symptom.slug, "xyz-symptom-mop", True)


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