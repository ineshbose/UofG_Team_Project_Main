<!-- PROJECT LOGO -->
<br />
<div align="center">
<p align="center">
  <img src="static/sleep_app/img/logo.png" alt="Logo" width="80" height="80">

  <h2 align="center">TrypAdvisor</h2>

  <p align="center">
    Sleep Sickness Surveillance App
    <br />
    <a href="http://trypadvisor.pythonanywhere.com/">View Demo</a>
    ·
    <a href="mailto:Walt.Adamson@glasgow.ac.uk">Report Bug</a>
    ·
    <a href="mailto:Walt.Adamson@glasgow.ac.uk">Request Feature</a>
    <br />
    <img alt="pipeline status" src="https://stgit.dcs.gla.ac.uk/tp3-2020-CS04/cs04-main/badges/master/pipeline.svg" />
    <img alt="coverage report" src="https://stgit.dcs.gla.ac.uk/tp3-2020-CS04/cs04-main/badges/master/coverage.svg" />
  </p>
</p>
</div>



<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Running](#running)
  * [Testing](#testing)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [SoCS Team Project H 2020 CS04](#socs-team-project-h-2020-cs04)



<!-- ABOUT THE PROJECT -->
## About The Project

Sleeping sickness is a disease that affects speakers of many different languages, and symptoms can vary by geographic location. As a result, this app:
* enables sleeping sickness researchers to easily make modifications (such as altering the text, asking different questions, or translating everything into a different language) without great levels of programming know-how;
* submits reports to should contain up-to-date records of all submissions, including answers to all questions and geographic location;

### Built With
* [Django](https://www.djangoproject.com/)
* [Bootstrap](https://getbootstrap.com)

_For more information, please refer to the [Wiki](https://stgit.dcs.gla.ac.uk/tp3-2020-CS04/cs04-main/-/wikis/home)_.



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

* git

The first step is to clone the repository in your preferred directory using
```sh
git clone https://stgit.dcs.gla.ac.uk/tp3-2020-CS04/cs04-main
cd cs04-main
```
This requires [Git](https://git-scm.com/); however, you can also download the repository as a
[zip](https://stgit.dcs.gla.ac.uk/tp3-2020-CS04/cs04-main/-/archive/master/cs04-main-master.zip),
[tar.gz](https://stgit.dcs.gla.ac.uk/tp3-2020-CS04/cs04-main/-/archive/master/cs04-main-master.tar.gz),
[tar.bz2](https://stgit.dcs.gla.ac.uk/tp3-2020-CS04/cs04-main/-/archive/master/cs04-main-master.tar.bz2) and
[tar](https://stgit.dcs.gla.ac.uk/tp3-2020-CS04/cs04-main/-/archive/master/cs04-main-master.tar).

* python / pip

A virtual environment is always a good idea.
```sh
python3 -m venv env
source env/scripts/activate
pip3 install -r requirements.txt
```

### Running

1. Make model migrations
```sh
python3 manage.py makemigrations
```
2. Reflect migrations to database
```sh
python3 manage.py migrate
```
3. Populate with data
```sh
python3 population_script.py
```
4. Run application
```sh
python3 manage.py runserver
```
Navigate to 127.0.0.1:8000 on a browser to view the application!

### Testing

Unit tests are in sleep_app/tests.py. Run them with
```sh
python3 manage.py test
```



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

[Dr. Walt Adamson](https://www.gla.ac.uk/researchinstitutes/bahcm/staff/waltadamson/#) - [Walt.Adamson@glasgow.ac.uk](mailto:Walt.Adamson@glasgow.ac.uk)

Project Link: [http://trypadvisor.pythonanywhere.com/](http://trypadvisor.pythonanywhere.com/)



<!-- Team Members -->
## SoCS Team Project H 2020 CS04
* Dr. Tim Storer _(Lecturer)_
* Hannah Mehravari _(Coach)_
* Amy Kidd
* Elizabeth Boswell
* Inesh Bose
* Jingqi Li
* Mihhail Pikkov