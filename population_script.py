import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sleep_surveillance.settings")

import django

django.setup()
from sleep_app.models import Symptom


def populate():
    symptom_list = [
        #       Member of public symptoms
        {
            "name": "Fever",
            "question": "Do you have a fever?",
            "answer_type": "bool",
            "symptom_type": "MOP",
            "image": "symptoms/fever.jpg",
        },
        {
            "name": "Muscle Aches",
            "question": "Do you experience muscle aches?",
            "answer_type": "bool",
            "symptom_type": "MOP",
            "image": "symptoms/muscle-aches.jpg",
        },
        {
            "name": "Fatigue",
            "question": "Do you experience fatigue?",
            "answer_type": "bool",
            "symptom_type": "MOP",
            "image": "symptoms/fatigue.jpg",
        },
        {
            "name": "Itchy Skin",
            "question": "Do you have itchy skin?",
            "answer_type": "bool",
            "symptom_type": "MOP",
            "image": "symptoms/itchy-skin.jpg",
        },
        {
            "name": "Sleep/Wake Disturbances",
            "question": "Do you experience sleep/wake disturbances?",
            "answer_type": "bool",
            "symptom_type": "MOP",
        },
        {
            "name": "Other Symptoms",
            "question": "Is there anything else you would like to report?",
            "answer_type": "text",
            "symptom_type": "MOP",
        },
        #   Healthcare worker symptoms. There are some duplicates here - the questions will be different if they're not addressing
        #   the patient directly
        {
            "name": "Fever",
            "question": "Does the patient have a fever?",
            "answer_type": "bool",
            "symptom_type": "HCW",
            "image": "symptoms/fever.jpg",
        },
        {
            "name": "Muscle Aches",
            "question": "Does the patient experience muscle aches?",
            "answer_type": "bool",
            "symptom_type": "HCW",
            "image": "symptoms/muscle-aches.jpg",
        },
        {
            "name": "Fatigue",
            "question": "Does the patient experience fatigue?",
            "answer_type": "bool",
            "symptom_type": "HCW",
            "image": "symptoms/fatigue.jpg",
        },
        {
            "name": "Itchy Skin",
            "question": "Does the patient have itchy skin?",
            "answer_type": "bool",
            "symptom_type": "HCW",
            "image": "symptoms/itchy-skin.jpg",
        },
        {
            "name": "Sleep/Wake Disturbances",
            "question": "Does the patient experience sleep/wake disturbances?",
            "answer_type": "bool",
            "symptom_type": "HCW",
        },
        {
            "name": "Swollen Lymph Nodes",
            "question": "Does the patient have swollen lymph nodes?",
            "answer_type": "bool",
            "symptom_type": "HCW",
        },
        {
            "name": "Anaemia",
            "question": "Is the person anaemic?",
            "answer_type": "bool",
            "symptom_type": "HCW",
        },
        {
            "name": "Seropositive for sleeping sickness",
            "question": "Is the patient seropositive for sleeping sickness?",
            "answer_type": "bool",
            "symptom_type": "HCW",
        },
        {
            "name": "Other Symptoms",
            "question": "Is there anything else you would like to report?",
            "answer_type": "text",
            "symptom_type": "HCW",
        },
        {
            "name": "Free entry",
            "question": "Please enter your observations.",
            "answer_type": "text",
            "symptom_type": "EOV",
        },
    ]

    for s in symptom_list:
        a_symptom = Symptom(
            name=s["name"],
            question=s["question"],
            answer_type=s["answer_type"],
            symptom_type=s["symptom_type"],
        )
        if "image" in s.keys():
            a_symptom.image = s["image"]
        a_symptom.save()

    # Start execution here!


if __name__ == "__main__":
    print("Starting sleep_app population script...")
    populate()
