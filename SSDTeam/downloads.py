from ssdteam.encryption import decrypt_post, decrypt_medical_record
from ssdteam.models import User, Post, Weight, BloodPressure
from ssdteam import db
from flask_login import current_user
import csv
from flask import send_file

def download_record(user_email, record_type):
    path = 'ExportedData.csv'
    user = User.query.filter_by(email=user_email).first()

    if record_type == 'Posts':
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

        with open(path, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'author', 'recipient', 'date_posted', 'title', 'content'])
            writer.writeheader()
            for post in posts:
                writer.writerow(post)

    elif record_type == 'Blood Pressure':
        user_id = user.id
        encrypted_bp = BloodPressure.query.filter_by(user_id=user_id).all()

        posts = decrypt_medical_record(encrypted_bp, user.key)

        with open(path, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'author', 'date_posted', 'record'])
            writer.writeheader()
            for post in posts:
                writer.writerow(post)

    elif record_type == 'Weight':
        user_id = user.id
        encrypted_weight = Weight.query.filter_by(user_id=user_id).all()

        posts = decrypt_medical_record(encrypted_weight, user.key)

        with open(path, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'author', 'date_posted', 'record'])
            writer.writeheader()
            for post in posts:
                writer.writerow(post)

    return send_file(path, as_attachment=True)

