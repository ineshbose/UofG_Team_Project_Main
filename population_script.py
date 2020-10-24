import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sleep_surveillance.settings')

import django
django.setup()
from sleep_app.models import Symptom

def populate():
    symptom_list = [
        {'name' : 'Fever',
         'question': 'Do you have a fever?',
         'answer_type' : 'bool',
         'image': 'symptoms/fever.jpg'},
        {'name' : 'Muscle Aches',
         'question': 'Do you experience muscle aches?',
         'answer_type': 'bool',
         'image': 'symptoms/muscle-aches.jpg'},
        {'name': 'Fatigue',
         'question': 'Do you experience fatigue?',
         'answer_type': 'bool',
         'image': 'symptoms/fatigue.jpg'},
        {'name': 'Itchy Skin',
         'question': 'Do you have itchy skin?',
         'answer_type': 'bool',
         'image':'symptoms/itchy-skin.jpg'},
        {'name': 'Sleep/Wake Disturbances',
         'question': 'Do you experience sleep/wake disturbances?',
         'answer_type': 'bool',},
        {'name': 'Other Symptoms',
         'question': 'Is there anything else you would like to report?',
         'answer_type': 'text'}
    ]

    for s in symptom_list:
        a_symptom = Symptom(name = s['name'], question=s['question'], answer_type = s['answer_type'])
        if 'image' in s.keys():
            a_symptom.image = s['image']
        a_symptom.save()

    # Start execution here!
if __name__ == '__main__':
    print('Starting sleep_app population script...')
    populate()