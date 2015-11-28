from wtforms import Form, StringField, TextAreaField, SelectField, DateField, RadioField, HiddenField, \
    SelectMultipleField, ValidationError
from wtforms.validators import DataRequired, Email, Length
from ..models import SurveyGroup
import datetime, re


class SurveyGroupCreationForm(Form):
    name = StringField('Survey Group Name', [DataRequired(), Length(min=4, max=255)])
    description = TextAreaField('Survey Group Description', [Length(max=500)])
    members = TextAreaField('Survey Group Members', [DataRequired()])

    def validate_members_email_list(self):
        """ validate mail addresses entered by user. return two lists: [good mail addresses, bad mail addresses] """

        good_mail_list = []
        bad_mail_list = []

        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
        mail_list = self.members.data.split(',')
        for mail_address in mail_list:
            mail_address = mail_address.strip()
            if EMAIL_REGEX.match(mail_address):
                good_mail_list.append(mail_address)
            elif mail_address != "":
                bad_mail_list.append(mail_address)

        return [good_mail_list, bad_mail_list]


class SurveyGroupMemberAddForm(Form):
    member_id = SelectMultipleField('Select Survey Group Members')
    # members list will be populated at runtime from controller


class SurveyAddForm(Form):
    title = StringField('Title', [Length(min=1, max=255)])
    question = TextAreaField('Question', [DataRequired(), Length(max=500)])
    creation_date = DateField('Creation Date', default=datetime.date.today())
    expiry_date = DateField('Expiry Date', [DataRequired()])
    survey_group_id = SelectField('Survey Group', [DataRequired()])
    expiry_date_ = HiddenField('Creation Date', default=datetime.date.today() + datetime.timedelta(days=1))


class SurveyForm(Form):
    answer = RadioField("", choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")])


class EditUserRoleForm(Form):
    user_role = SelectField('User Role', [DataRequired()])


class UserProfileEditForm(Form):
    name = StringField('Full Name', [Length(min=4, max=255)])
    bio = TextAreaField('Bio', [Length(max=500)])