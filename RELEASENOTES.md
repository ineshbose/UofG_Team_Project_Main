# RELEASE NOTES

This is version 1.0 of TrypAdvisor.

## Features:
- Forms with questions about sleeping sickness symptoms. They are automatically generated from the database. Different types of users can be asked different questions.
- An account system which enables researchers, entomologists and vets to view the users' data, and which lets admins perform administrative tasks. Admins need to verify other accounts. Members of the public do not have an account.
- A table to view the data that users have entered (only accessible to logged-in users).
- The table data can be exported as a CSV file (only accessible to logged-in users).
- A map to view answered forms location markers (only accessible to logged-in users).
- A REST API for automated access to the web-app's functionality.
- Site content can be translated.

For an in-depth description of features refer to our [wiki](https://stgit.dcs.gla.ac.uk/tp3-2020-CS04/cs04-main/-/wikis/home). The [user guide](https://stgit.dcs.gla.ac.uk/tp3-2020-CS04/cs04-main/-/wikis/User-instructions/General-User-Guide) describes the features relevant to admin users.

## Known Bugs and Issues:
- If the page is closed while answering the form, the entry will still be added to the database with remaining questions answered as blank. If a user wishes to close the form without submitting, they have to use the designated button.


