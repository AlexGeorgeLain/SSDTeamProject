from ssdteam import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
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

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}', '{self.role}', '{self.key}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    recipient = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

"""HEALTH TABLES NEXT"""

class BloodPressure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Weight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def delete_user_from_db(email):
    user = User.query.filter_by(email=email).first()

    if user:
        posts_received = Post.query.filter_by(recipient=user.email).all()
        posts = Post.query.filter_by(user_id=user.id).all()
        blood_pressures = BloodPressure.query.filter_by(user_id=user.id).all()
        weights = Weight.query.filter_by(user_id=user.id).all()

        for weight in weights:
            db.session.delete(weight)

        for bp in blood_pressures:
            db.session.delete(bp)

        for post in posts:
            db.session.delete(post)

        for post in posts_received:
            db.session.delete(post)

        db.session.delete(user)

        db.session.commit()
