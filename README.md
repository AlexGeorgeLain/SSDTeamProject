# SSD Team 4 Project Read Me


### Requirements and Running

This project has been written using Python 3.9, taking advantage of the Flask web framework. 
A full list of the packages used in this project can be found in the _requirements.txt_
file. These packages can be installed in your own virtual environment using the
`$ pip install -r requirements.txt` command.

The server can be started by using the `$ python run.py` command while in the project
root directory. Once the server is running, the web app can be accessed by navigating to 
http://127.0.0.1:5000 in a web browser. There are three accounts in the default database
which can be used to log in to the app. No functionality is available to unauthorised users.

These default logins are: 

| Email               | Password            | Role                |
| ------------------- | ------------------- | ------------------- |
| admin@email.com     | password            | Admin               |
| astro@email.com     | testing             | Astronaut           |
| doc@email.com       | test123             | Medic               |


### System Functionality
The application is designed to allow the astronauts on board the International Space
Station to be able to securely send health data to medical staff on the ground. To 
demonstrate this functionality we have chosen blood pressure and weight as two health
metrics which can be input. The system also allows the astronauts and medics to exchange 
private messages. All medical records and messages are encrypted using Fernet symmetric 
encryption.

The system makes use of three roles (Admin, Astronaut, and Medic) to limit the access that
each user. For example, one astronaut cannot view another's medical data or private
messages. Due to the expected use of the application we have also chosen to not allow users
to sign up for their own account. Only an admin user can register new user accounts. Users
can delete their own account using the API, and an admin may delete any user by using
the web app or API.

In addition to viewing the messages and records in the web app, users may also download any
of the data they have access to as a csv file.


### REST API


### Testing


### Further Improvements and Limitations