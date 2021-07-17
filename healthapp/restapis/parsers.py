from flask_restful import reqparse

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
