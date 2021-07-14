from ssdteam import app, db, bcrypt, api
from ssdteam.models import User, Post, BloodPressure, Weight, delete_user_from_db
from ssdteam.encryption import encrypt_post, encrypt_medical_record, decrypt_medical_record, decrypt_post
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from cryptography.fernet import Fernet
import jwt
from datetime import datetime, timedelta

roles = ['Admin', 'Astronaut', 'Medic']

user_get_args = reqparse.RequestParser()
user_get_args.add_argument('email', type=str, help='User email required', required=True)
user_get_args.add_argument('token', type=str, help='Auth token required', required=True)

user_put_args = reqparse.RequestParser()
user_put_args.add_argument('email', type=str, help='User email required', required=True)
user_put_args.add_argument('first_name', type=str, help='User first name required', required=True)
user_put_args.add_argument('last_name', type=str, help='User last name required', required=True)
user_put_args.add_argument('role', type=str, help=f'User role required. Must be in {roles}', required=True)
user_put_args.add_argument('password', type=str, help='User password required', required=True)
user_put_args.add_argument('token', type=str, help='Auth token required', required=True)

user_patch_args = reqparse.RequestParser()
user_patch_args.add_argument('email', type=str, help='User email required', required=True)
user_patch_args.add_argument('new_email', type=str, help='User email')
user_patch_args.add_argument('first_name', type=str, help='User first name')
user_patch_args.add_argument('last_name', type=str, help='User last name')
user_patch_args.add_argument('role', type=str, help=f'User role must be in {roles}')
user_patch_args.add_argument('password', type=str, help='User password')
user_patch_args.add_argument('token', type=str, help='Auth token required', required=True)

user_delete_args = reqparse.RequestParser()
user_delete_args.add_argument('email', type=str, help='User email required', required=True)
user_delete_args.add_argument('token', type=str, help='Auth token required', required=True)

user_fields = {
    'email': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
	'role': fields.String
}

login_args = reqparse.RequestParser()
login_args.add_argument('email', type=str, help='User email required', required=True)
login_args.add_argument('password', type=str, help='User password required', required=True)

def check_token(token):
	try:
		data = jwt.decode(token, app.config['SECRET_KEY'], 'HS256')

		current_user = User.query.filter_by(email=data['email']).first()
		return current_user

	except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
		return abort(403, message='Invalid token. Please login.')


def check_user_role(current_user, role):

	if current_user.role != role:
		abort(403, message='Access denied. Invalid user role.')


class LoginApi(Resource):
	def post(self):
		args = login_args.parse_args()
		user = User.query.filter_by(email=args['email']).first()

		if user and bcrypt.check_password_hash(user.password, args['password']):
			token = jwt.encode({'email': user.email,
								'exp': datetime.utcnow() + timedelta(seconds=5)},
								app.config['SECRET_KEY'], algorithm='HS256')

			return {'token': token}

		return {'message': 'Login error. Check username and password.'}


api.add_resource(LoginApi, '/api/login')


class UserApi(Resource):
	def __init__(self):
		self.user_roles = ['Admin', 'Astronaut', 'Medic']

	@marshal_with(user_fields)
	def get(self):
		args = user_get_args.parse_args()

		current_user = check_token(args['token'])
		check_user_role(current_user, 'Admin')

		if args['email'] == 'all':
			users = User.query.all()
			return users

		else:
			user = User.query.filter_by(email=args['email']).first()
			if not user:
				abort(404, message="Could not find user")
			return user

	@marshal_with(user_fields)
	def put(self):
		args = user_put_args.parse_args()

		current_user = check_token(args['token'])
		check_user_role(current_user, 'Admin')

		user = User.query.filter_by(email=args['email']).first()

		if user:
			abort(409, message=f"User with the email {args['email']} already exists")

		if args['role'] not in self.user_roles:
			abort(403, message=f'User role must in {self.user_roles}.')

		hashed_pw = bcrypt.generate_password_hash(args['password']).decode('utf-8')
		new_user = User(email=args['email'], first_name=args['first_name'], last_name=args['last_name'],
						role=args['role'], password=hashed_pw, key=Fernet.generate_key().decode('utf-8'))

		db.session.add(new_user)
		db.session.commit()

		return new_user, 201

	@marshal_with(user_fields)
	def patch(self):
		args = user_patch_args.parse_args()

		current_user = check_token(args['token'])
		check_user_role(current_user, 'Admin')

		user = User.query.filter_by(email=args['email']).first()

		if not user:
			abort(404, message="User does not exist, cannot update.")

		if args['new_email']:
			user.email = args['new_email']

		if args['first_name']:
			user.first_name = args['first_name']

		if args['last_name']:
			user.last_name = args['last_name']

		if args['role']:
			if args['role'] not in self.user_roles:
				abort(403, message=f'User role must in {self.user_roles}.')
			user.role = args['role']

		if args['password']:
			hashed_pw = bcrypt.generate_password_hash(args['password']).decode('utf-8')
			user.password = hashed_pw

		db.session.commit()

		return user

	def delete(self):
		args = user_delete_args.parse_args()

		current_user = check_token(args['token'])
		check_user_role(current_user, 'Admin')

		user = User.query.filter_by(email=args['email']).first()

		if not user:
			abort(404, message="User does not exist, cannot be deleted.")

		delete_user_from_db(args['email'])
		return {'message': 'User Deleted'}


api.add_resource(UserApi, '/api/user')
