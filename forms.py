from wtforms import *
from wtforms.ext.sqlalchemy.fields import QuerySelectField
import datetime#, timedelta


class UserRegistrationForm(Form):
    name = StringField('Full Name', [validators.Length(min=4, max=255)])
    email = StringField('Email Address', [validators.Email(), validators.Length(max=255)])
    bio = TextAreaField('Bio', [validators.optional(), validators.Length(max=500)])
    role_id = SelectField('User Role')  # user roles drop-down will be populated at runtime from controller


class SurveyGroupCreationForm(Form):
    name = StringField('Survey Group Name', [validators.Length(min=4, max=255)])
    description = TextAreaField('Description', [validators.optional(), validators.Length(max=500)])


class SurveyGroupMemberAddForm(Form):
    member_id = SelectMultipleField('Select Survey Group Members')
    # members list will be populated at runtime from controller


class SurveyAddForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=255)])
    question = TextAreaField('Question', [validators.InputRequired(), validators.Length(max=500)])
    creation_date = DateField('Creation Date', default=datetime.date.today())
    expiry_date = DateField('Expiry Date', [validators.InputRequired()])
    survey_group_id = SelectField('Survey Group')
    expiry_date_ = HiddenField('Creation Date', default=datetime.date.today()+datetime.timedelta(days=1))


if __name__ == '__main__':
    a = "test"
    form = SurveyAddForm()
    print(form.expiry_date)
    print(form.expiry_date_)

