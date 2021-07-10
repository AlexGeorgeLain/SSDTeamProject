from ssdteam import db, bcrypt
from ssdteam.models import User, Post
from cryptography.fernet import Fernet


db.drop_all()

db.create_all()

hashed_password_admin = bcrypt.generate_password_hash('password').decode('utf-8')
user_admin = User(first_name='Test', last_name='Admin', email='admin@email.com', password=hashed_password_admin, role='Admin', key=Fernet.generate_key().decode('utf-8'))

hashed_password_astro = bcrypt.generate_password_hash('testing').decode('utf-8')
user_astro = User(first_name='Astro', last_name='Naut', email='astro@email.com', password=hashed_password_astro, role='Astronaut', key=Fernet.generate_key().decode('utf-8'))

hashed_password_med = bcrypt.generate_password_hash('test123').decode('utf-8')
user_med = User(first_name='Doctor', last_name='Zoidberg', email='doc@email.com', password=hashed_password_med, role='Medic', key=Fernet.generate_key().decode('utf-8'))

db.session.add(user_admin)
db.session.add(user_astro)
db.session.add(user_med)

db.session.commit()

print(User.query.all())
