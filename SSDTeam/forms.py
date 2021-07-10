from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ssdteam.models import User
from flask_wtf.file import FileField, FileAllowed

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = StringField("Role: 'Admin', 'Astronaut', or 'Medic'", validators=[DataRequired()] )
    submit = SubmitField('Register User')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use')

    def validate_role(self, role):
        if role.data not in ['Admin', 'Astronaut', 'Medic']:
            raise ValidationError("Role must be either 'Admin', 'Astronaut', or 'Medic'")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    recipient = StringField('Recipient', validators=[DataRequired(), Email()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

    def validate_recipient(self, recipient):
        user = User.query.filter_by(email=recipient.data).first()
        if not user:
            raise ValidationError('Recipient email not registered')


class BloodPressureForm(FlaskForm):
    blood_pressure = StringField('Blood Pressure', validators=[DataRequired(), Length(min=5, max=7)])
    submit = SubmitField('Submit')

    def validate_bp(self, blood_pressure):
        """best way to validate?"""
        pass


class WeightForm(FlaskForm):
    weight = StringField('Weight', validators=[DataRequired(), Length(min=2, max=5)])
    submit = SubmitField('Submit')

    def validate_weight(self, weight):
        """best way to validate?"""
        pass