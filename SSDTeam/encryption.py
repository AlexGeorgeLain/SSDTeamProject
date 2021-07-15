"""Module containing functions for encrypting/decrypting data.

Functions:
    encrypt_medical_record -- encrypts a given medical record using the user key.
    decrypt_medical_record -- decrypts a number of posts using the key.
    encrypted_post -- encrypts a post using the recipient's key.
    decrypt_post -- decrypts a number of posts using the key.
"""

from cryptography.fernet import Fernet
from ssdteam.models import User


def encrypt_medical_record(new_entry, user_key):
    """Encrypts a record using the given key.

    Keyword arguments:
        new_entry -- the new record entry that is to be encrypted.
        user_key -- the key of the user that the record is associated with.
    """

    encoded_data = new_entry.encode()
    encrypted_data = Fernet(user_key.encode()).encrypt(encoded_data).decode('utf-8')
    return encrypted_data


def decrypt_medical_record(encrypted_posts, key):
    """Decrypts records using the given key.

    Keyword arguments:
         encrypted_posts -- posts to be decrypted.
         key -- encryption key associated with the records.
    """

    decrypted_posts = []

    for post in encrypted_posts:
        encrypted_data = post.record.encode()
        decrypted_data = Fernet(key.encode()).decrypt(encrypted_data).decode('utf-8')

        decrypted_posts.append({'id': post.id,
                                'author': post.author.email,
                                'date_posted': post.date_posted.strftime('%Y-%m-%d'),
                                'record': decrypted_data})

    return decrypted_posts


def encrypt_post(post, recipient):
    """Encrypts a user post using the recipient's key.

    Keyword arguments:
        post -- The post to be encrypted.
        recipient -- the recipient of the post
    """

    encryption_key = User.query.filter_by(email=recipient).first().key
    encoded_data = post.encode()
    encrypted_post = Fernet(encryption_key.encode()).encrypt(encoded_data).decode('utf-8')

    return encrypted_post


def decrypt_post(encrypted_posts, key):
    """Decrypts posts using the given key.

    Keyword arguments:
          encrypted_posts -- the posts to be decrypted.
          key -- recipient key associated with the encrypted posts.
    """

    decrypted_posts = []

    for post in encrypted_posts:
        encrypted_data = post.content.encode()
        decrypted_data = Fernet(key.encode()).decrypt(encrypted_data).decode('utf-8')

        decrypted_posts.append({'id': post.id,
                                'author': post.author.email,
                                'recipient': post.recipient,
                                'date_posted': post.date_posted.strftime('%Y-%m-%d'),
                                'title': post.title,
                                'content': decrypted_data})

    return decrypted_posts
