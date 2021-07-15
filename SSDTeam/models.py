"""Module containing the data models for the app.

Classes:
    User -- database model for users.
    Post -- database model for user posts.
    BloodPressure -- database model for blood pressure records.
    Weight -- database model for weight records.

Functions:
    delete_user_from_db -- deletes a user and all associated data from the database.
"""

from datetime import datetime
from flask_login import UserMixin
from ssdteam import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Loads user as current_user

    Keyword args:
        user_id -- id of logged in user.
    """

    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """User table in database. Stores user information"""

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    key = db.Column(db.String, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    blood_pressure = db.relationship('BloodPressure', backref='author', lazy=True)
    weight = db.relationship('Weight', backref='author', lazy=True)


class Post(db.Model):
    """Post table in database. Stores all interaction between users."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    recipient = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class BloodPressure(db.Model):
    """Blood pressure table in database. Stores blood pressure records for all astronauts."""

    id = db.Column(db.Integer, primary_key=True)
    record = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Weight(db.Model):
    """Weight table in database. Stores weight records for all astronauts."""

    id = db.Column(db.Integer, primary_key=True)
    record = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def delete_user_from_db(email):
    """Deletes user and all associated data.

    Keyword args:
        email -- email of the user to be deleted.
    """

    user = User.query.filter_by(email=email).first()

    if user:
        posts_received = Post.query.filter_by(recipient=user.email).all()
        posts = Post.query.filter_by(user_id=user.id).all()
        blood_pressures = BloodPressure.query.filter_by(user_id=user.id).all()
        weights = Weight.query.filter_by(user_id=user.id).all()

        for weight in weights:
            db.session.delete(weight)

        for blood_pressure in blood_pressures:
            db.session.delete(blood_pressure)

        for post in posts:
            db.session.delete(post)

        for post in posts_received:
            db.session.delete(post)

        db.session.delete(user)

        db.session.commit()
