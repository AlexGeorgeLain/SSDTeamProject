# SSD Team 4 Project Read Me


### Requirements and Running

This project has been written using Python 3.9, taking advantage of the Flask web framework. A full list of the 
packages used in this project can be found in the _requirements.txt_ file. These packages can be installed in your 
own virtual environment using the `$ pip install -r requirements.txt` command. All the packages and technologies used
in the development of this project are open-source as required by the project specifications.

The server can be started by using the `$ python run.py` command while in the project root directory. Once the server 
is running, the web app can be accessed by navigating to http://127.0.0.1:5000 in a web browser. There are three 
accounts in the default database which can be used to log into the app. No functionality is available to unauthorised 
users.

These default logins are: 

| Email               | Password            | Role                |
| ------------------- | ------------------- | ------------------- |
| admin@email.com     | password            | Admin               |
| astro@email.com     | testing             | Astronaut           |
| doc@email.com       | test123             | Medic               |


### System Functionality
The application is designed to allow the astronauts on board the International Space Station to be able to securely 
send health data to medical staff on the ground. To demonstrate this functionality we have chosen blood pressure and 
weight as two health metrics which can be input. The system also allows the astronauts and medics to exchange private 
messages. All medical records and messages are encrypted using Fernet symmetric encryption.

The system makes use of three roles (Admin, Astronaut, and Medic) to limit the access that each user. For example, one 
astronaut cannot view another's medical data or private messages. Due to the expected use of the application we have 
also chosen to not allow users to sign up for their own account. Only an admin user can register new user accounts. 
Users can delete their own account using the API, and an admin may delete any user by using the web app or API.

In addition to viewing the messages and records in the web app, users may also download any
of the data they have access to as a csv file.


### REST API
 Alongside the web api, we have also developed a REST API. All data is sent and recieved as JSON.
 
The API contains the following resources:

| Resource                  | Methods                 |
| ------------------------- | ----------------------- |
| /api/login                | PUT                     | 
| /api/user                 | GET, PUT, PATCH, DELETE |
| /api/record/<record_type> | GET, PUT                | 
| /api/post                 | GET, PUT                | 

`PUT /api/login` allows users to log in by sending their email and password as arguments with the request. This request
will return a JSON web token which must be sent with all other requests to authenticate the user.

`GET /api/user` allows an authenticated user to view details about various users registered in the database, providing
they have the correct permissions.

`PUT /api/user`allows an admin user to register a new user account.

`PATCH /api/user` allows an admin user to update the account details of any user registered in the database.

`DELETE /api/user` allows an admin user to delete any user from the database, along with all their associated records.
This also allows a user to delete their own account and records.

`GET /api/record/<record_type>` allows a user to view their own records. Also allows an admin or medic to view
the records of any astronaut.

`PUT /api/record/<record_type>` allows an astronaut to add a new record to the database.

`GET /api/post` allows users to view all their private messages, either to and from all other users, or a specific
user.

`PUT /api/post` allows a user to send a private message to another user in the database.

Full examples of the API use are available in the _/healthapp/restapi/tests_ folder.

### Testing



### Further Improvements and Limitations