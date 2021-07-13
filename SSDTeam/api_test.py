import requests
from ssdteam.rebuild_db import rebuild_db

if __name__ == "__main__":
    rebuild_db()

    BASE = 'http://127.0.0.1:5000/'

    print('Get requests')

    response = requests.get(BASE + '/api/user', {'email': 'all'})
    print(response.json())

    response = requests.get(BASE + '/api/user', {'email': 'errortest'})
    print(response.json())

    response = requests.get(BASE + '/api/user', {'email': 'admin@email.com'})
    print(response.json())

    response = requests.get(BASE + '/api/user')
    print(response.json())

    print('')
    print('Put requests')

    response = requests.put(BASE + '/api/user', {'email': 'new@email.com', 'first_name': 'New', 'last_name': 'Name',
                                                 'role': 'Astronaut', 'password': 'password'})
    print(response.json())

    response = requests.put(BASE + '/api/user', {'email': 'new2@email.com', 'first_name': 'New', 'last_name': 'Name',
                                                 'role': 'Astro', 'password': 'password'})
    print(response.json())

    response = requests.put(BASE + '/api/user', {'email': 'new@email.com', 'first_name': 'New', 'last_name': 'Name',
                                                 'role': 'Astronaut', 'password': 'password'})
    print(response.json())

    print('')
    print('Patch requests')

    response = requests.patch(BASE + '/api/user', {'email': 'new@email.com', 'new_email': 'updated@email.com'})
    print(response.json())

    response = requests.patch(BASE + '/api/user', {'email': 'new@email.com', 'first_name': 'updated name'})
    print(response.json())

    response = requests.patch(BASE + '/api/user', {'email': 'upodated@email.com', 'role': 'medic'})
    print(response.json())

    response = requests.patch(BASE + '/api/user', {'email': 'updated@email.com', 'role': 'Medic'})
    print(response.json())

    response = requests.patch(BASE + '/api/user', {'email': 'updated@email.com', 'password': 'newpassword'})
    print(response.json())

    print('')
    print('Delete requests')

    response = requests.delete(BASE + '/api/user', data={'email': 'new@email.com'})
    print(response.json())

    response = requests.delete(BASE + '/api/user', data={'email': 'updated@email.com'})
    print(response.json())

    response = requests.get(BASE + '/api/user', {'email': 'all'})
    print(response.json())
