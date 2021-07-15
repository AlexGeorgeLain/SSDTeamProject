from ssdteam import app, db, bcrypt, api
from ssdteam.models import User, Post, BloodPressure, Weight, delete_user_from_db
from ssdteam.encryption import encrypt_post, encrypt_medical_record, decrypt_medical_record, decrypt_post
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from cryptography.fernet import Fernet
from flask import jsonify
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

record_post_args = reqparse.RequestParser()
record_post_args.add_argument('record', type=str, help='Record required', required=True)
record_post_args.add_argument('token', type=str, help='Auth token required', required=True)

record_get_args = reqparse.RequestParser()
record_get_args.add_argument('token', type=str, help='Auth token required', required=True)
record_get_args.add_argument('email', type=str, help='User email required', required=True)

post_get_args = reqparse.RequestParser()
post_get_args.add_argument('token', type=str, help='Auth token required', required=True)
post_get_args.add_argument('email', type=str, help='User email required')

post_post_args = reqparse.RequestParser()
post_post_args.add_argument('token', type=str, help='Auth token required', required=True)
post_post_args.add_argument('email', type=str, help='User email required', required=True)
post_post_args.add_argument('content', type=str, help='Content required', required=True)
post_post_args.add_argument('title', type=str, help='Title required', required=True)


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

		if current_user.email == args['email']:
			delete_user_from_db(current_user.email)
			return {'message': 'User Deleted'}

		check_user_role(current_user, 'Admin')

		user = User.query.filter_by(email=args['email']).first()

		if not user:
			abort(404, message="User does not exist, cannot be deleted.")

		delete_user_from_db(args['email'])
		return {'message': 'User Deleted'}


api.add_resource(UserApi, '/api/user')


class RecordApi(Resource):
	def __init__(self):
		self.record_types = ['blood_pressure', 'weight']

	def get(self, record_type):
		args = record_get_args.parse_args()

		current_user = check_token(args['token'])

		if record_type == 'blood_pressure':
			if current_user.email == args['email']:
				encrypted_bp = BloodPressure.query.filter_by(user_id=current_user.id).order_by(
					BloodPressure.date_posted.desc()).all()

				posts = decrypt_medical_record(encrypted_bp, User.query.filter_by(email=current_user.email).first().key)

				return jsonify(posts)

			if current_user.role in ['Admin', 'Medic']:
				user = User.query.filter_by(email=args['email']).first()
				encrypted_bp = BloodPressure.query.filter_by(user_id=user.id).order_by(
					BloodPressure.date_posted.desc()).all()

				posts = decrypt_medical_record(encrypted_bp, User.query.filter_by(email=args['email']).first().key)

				return jsonify(posts)

		if record_type == 'weight':
			if current_user.email == args['email']:
				encrypted_weight = Weight.query.filter_by(user_id=current_user.id).order_by(
					Weight.date_posted.desc()).all()

				posts = decrypt_medical_record(encrypted_weight, User.query.filter_by(email=current_user.email).first().key)

				return jsonify(posts)

			if current_user.role in ['Admin', 'Medic']:
				user = User.query.filter_by(email=args['email']).first()
				encrypted_weight = Weight.query.filter_by(user_id=user.id).order_by(
					Weight.date_posted.desc()).all()

				posts = decrypt_medical_record(encrypted_weight, User.query.filter_by(email=args['email']).first().key)

				return jsonify(posts)

		return abort(403, message='Access denied.')

	def post(self, record_type):
		args = record_post_args.parse_args()

		current_user = check_token(args['token'])
		check_user_role(current_user, 'Astronaut')

		if record_type == 'blood_pressure':
			encrypted_blood_pressure = encrypt_medical_record(args['record'], current_user.key)

			bp = BloodPressure(record=encrypted_blood_pressure, user_id=current_user.id)
			db.session.add(bp)
			db.session.commit()

			return {'message': 'Blood pressure record added.'}

		if record_type == 'weight':
			encrypted_weight = encrypt_medical_record(args['record'], current_user.key)

			weight = Weight(record=encrypted_weight, user_id=current_user.id)
			db.session.add(weight)
			db.session.commit()

			return {'message': 'Weight record added.'}

		return {'message': f'record_type must be in {self.record_types}.'}


api.add_resource(RecordApi, '/api/record/<string:record_type>')


class PostApi(Resource):
	def get(self):
		args = post_get_args.parse_args()

		current_user = check_token(args['token'])

		if not args['email']:
			encrypted_posts = db.session.query(Post) \
				.where((Post.recipient == current_user.email) | (Post.user_id == current_user.id)) \
				.order_by(Post.date_posted.desc()).all()

			posts = []

			for post in encrypted_posts:
				post_list = [post]
				if post_list[0].recipient == current_user.email:
					posts.append(decrypt_post(post_list, current_user.key)[0])

				else:
					user = User.query.filter_by(email=post.recipient).first()
					posts.append(decrypt_post(post_list, user.key)[0])

			return jsonify(posts)

		user = User.query.filter_by(email=args['email']).first()
		encrypted_posts = db.session.query(Post) \
			.where(((Post.user_id == user.id) & (Post.recipient == current_user.email))
					| ((Post.user_id == current_user.id) & (Post.recipient == user.email))) \
			.order_by(Post.date_posted.desc()).all()

		posts = []

		for post in encrypted_posts:
			post_list = [post]
			if post_list[0].recipient == current_user.email:
				posts.append(decrypt_post(post_list, current_user.key)[0])

			if post_list[0].recipient == user.email:
				posts.append(decrypt_post(post_list, user.key)[0])

		return jsonify(posts)

	def post(self):
		args = post_post_args.parse_args()

		current_user = check_token(args['token'])
		user = User.query.filter_by(email=args['email'])

		if not user:
			return {'message': 'Recipient email not found.'}

		encrypted_content = encrypt_post(args['content'], args['email'])

		post = Post(recipient=args['email'], title=args['title'], content=encrypted_content,
					author=current_user)

		db.session.add(post)
		db.session.commit()

		return {'message': f'Post sent to {args["email"]}.'}


api.add_resource(PostApi, '/api/post')
