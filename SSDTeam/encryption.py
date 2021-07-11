from cryptography.fernet import Fernet
from ssdteam.models import User


def encrypt_medical_record(new_entry, user_key):
    encoded_data = new_entry.encode()
    f = Fernet(user_key.encode())
    encrypted_data = f.encrypt(encoded_data).decode('utf-8')
    return encrypted_data


def decrypt_medical_record(encrypted_posts, key):
    decrypted_posts = []

    for post in encrypted_posts:
        f = Fernet(key.encode())
        encrypted_data = post.record.encode()
        decrypted_data = f.decrypt(encrypted_data).decode('utf-8')

        decrypted_posts.append({'author': post.author.email,
                                'date_posted': post.date_posted.strftime('%Y-%m-%d'),
                                'id': post.user_id,
                                'record': decrypted_data})

    return decrypted_posts


def encrypt_post(post, recipient):
    encryption_key = User.query.filter_by(email=recipient).first().key
    encoded_data = post.encode()
    f = Fernet(encryption_key.encode())
    encrypted_post = f.encrypt(encoded_data).decode('utf-8')

    return encrypted_post


def decrypt_post(encrypted_posts, key):
    decrypted_posts = []

    for post in encrypted_posts:
        f = Fernet(key.encode())
        encrypted_data = post.content.encode()
        decrypted_data = f.decrypt(encrypted_data).decode('utf-8')

        decrypted_posts.append({'author': post.author.email,
                                'date_posted': post.date_posted.strftime('%Y-%m-%d'),
                                'id': post.user_id,
                                'title': post.title,
                                'content': decrypted_data})

    return decrypted_posts
