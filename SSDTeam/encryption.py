from cryptography.fernet import Fernet

def generate_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)


def load_key():
    """
    Load the previously generated key
    """
    return open("secret.key", "rb").read()


def encrypt_message(message):
    """
    Encrypts a message
    """
    key = Fernet.generate_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message).decode('utf-8')
    encrypted_message1 = encrypted_message.encode()
    decrypted_message = f.decrypt(encrypted_message1).decode('utf-8')

    print(key)
    print(encrypted_message)
    print(decrypted_message)


def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    print(decrypted_message.decode())


if __name__ == "__main__":
    encrypt_message("encrypt this message")

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


