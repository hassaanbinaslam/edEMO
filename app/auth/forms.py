from wtforms import Form, StringField, PasswordField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo
from ..models import User


class LoginForm(Form):
    email = StringField('Email', validators=[Email(), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired()])


class RegistrationForm(Form):
    name = StringField('Full Name', [Length(min=4, max=255)])
    email = StringField('Email Address', [Email(), Length(max=255)])
    bio = TextAreaField('Bio', [Length(max=500)])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Provided email address is already registered.')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Email(), Length(max=255)])


class PasswordResetForm(Form):
    email = StringField('Email Address', [Email(), Length(max=255)])

    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Provided email address is not registered.')