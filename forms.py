from wtforms import *
from wtforms.ext.sqlalchemy.fields import QuerySelectField


class UserRegistrationForm(Form):
    name = StringField('Full Name', [validators.Length(min=4, max=255)])
    email = StringField('Email Address', [validators.Email(), validators.Length(max=255)])
    bio = TextAreaField('Bio', [validators.optional(), validators.Length(max=500)])
    role_id = SelectField('User Role') # user roles drop-down will be populated at runtime from controller

if __name__ == '__main__':
    a = "test"
    form_user_registration = UserRegistrationForm()
    print(form_user_registration.name)
    print(form_user_registration.email)
    print(form_user_registration.bio)
    print
