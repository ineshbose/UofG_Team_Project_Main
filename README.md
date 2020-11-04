# CS04 Main Repository

This is the main repository for the Sleeping Sickness Surveillance app. This app will enable researchers to track sleeping sickiness outbreaks by allowing 
healthcare workers, members of the public and entomologists/vets to enter sleeping sickness symptoms.

Clone the repository with `git clone https://stgit.dcs.gla.ac.uk/tp3-2020-CS04/cs04-main.git`

Install all the required packages using `pip install -r requirements.txt`.

Set up the database with `python manage.py makemigrations sleep_app`
                          `python manage.py migrate`
                          `python population_script.py`
                        
Finally, run `python manage.py runserver` and nagivate to `http://127.0.0.1:8000/form/` to view the app.