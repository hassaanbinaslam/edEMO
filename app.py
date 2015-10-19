# ----- Imports -----#
import os
from flask import Flask, request, render_template, url_for, redirect
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from forms import *
from models import *

from models import Base

# ----- App Config. and DB setup -----#
app = Flask(__name__)
bootstrap = Bootstrap(app)
PWD = os.path.abspath(os.curdir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/edEMO.db'.format(PWD)
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
db.Model = Base
db.create_all()
# db.session.query(UserRole).delete()
# db.session.query(User).delete()
# db.session.query(SurveyGroup).delete()
# db.session.query(SurveyGroupMember).delete()
# db.session.query(Survey).delete()
if db.session.query(UserRole).count() == 0:
    db.session.add(UserRole(1, "SYSTEM_ADMIN"))
    db.session.add(UserRole(2, "SURVEY_ADMIN"))
    db.session.add(UserRole(3, "SURVEY_TAKER"))
    db.session.commit()
if db.session.query(User).count() == 0:
    db.session.add(User("admin@localhost", "Admin", "System Admin", 1))
    db.session.add(User("user1@localhost", "Survey Admin", "Survey Admin", 2))
    db.session.add(User("user2@localhost", "Survey Taker 1", "Survey Taker 1", 3))
    db.session.add(User("user3@localhost", "Survey Taker 2", "Survey Taker 2", 3))
    db.session.commit()
if db.session.query(SurveyGroup).count() == 0:
    db.session.add(SurveyGroup("CS6460", "EdTech", 2))
    db.session.commit()
if db.session.query(SurveyGroupMember).count() == 0:
    db.session.add(SurveyGroupMember(1, 3))
    db.session.add(SurveyGroupMember(1, 3))
    db.session.commit()
if db.session.query(Survey).count() == 0:
    db.session.add(Survey("First Survey", "Hello World?", datetime.date.today(),
                          (datetime.date.today() + datetime.timedelta(days=1)), 2, 1))

# ----- Controllers -----#
@app.route('/')
def home():
    return render_template('pages/home.html')


@app.route('/login')
def login():
    return render_template('pages/login.html')


@app.route('/profile')
def profile():
    return render_template('pages/view-profile.html')


@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    """ Provide HTML form to register new user """
    form = UserRegistrationForm(request.form)
    roles = db.session.query(UserRole).all()
    user_roles_available = []
    for role in roles:
        user_roles_available.append((str(role.id), role.name))
    form.role_id.choices = user_roles_available
    if request.method == 'POST' and form.validate():
        new_user = User()
        form.populate_obj(new_user)
        db.session.add(new_user)
        db.session.commit()
        # Success. Redirect user to full users list.
        return redirect(url_for('home'))
    # Load the page. If page was submitted and contain errors then load it with errors.
    return render_template('pages/user-register.html', form=form)
    # return render_template('pages/test.html')


@app.route('/survey/group/add', methods=['GET', 'POST'])
def survey_group_add():
    """ Provide HTML form to create new survey group """
    form = SurveyGroupCreationForm(request.form)
    current_user_id = 2  # Temporary. Needs to be fixed
    if request.method == 'POST' and form.validate():
        new_survey_group = SurveyGroup()
        form.populate_obj(new_survey_group)
        new_survey_group.creator_id = current_user_id
        db.session.add(new_survey_group)
        db.session.commit()
        # Success. Redirect user to full survey group list.
        return redirect(url_for('home'))
    # Load the page. If page was submitted and contain errors then load it with errors.
    return render_template('pages/survey-group-add.html', form=form)


@app.route('/survey/group/list')
def survey_group_list():
    current_user_id = 2  # Temporary. Needs to be fixed
    survey_group_list = db.session.query(SurveyGroup).filter(SurveyGroup.creator_id == current_user_id)
    return render_template('pages/survey-group-list.html', survey_group_list=survey_group_list)


@app.route('/survey/group/<int:survey_group_id>/member/add', methods=['GET', 'POST'])
def survey_group_member_add(survey_group_id):
    """ Provide HTML form to create new survey group """
    current_user_id = 2  # Temporary. Needs to be fixed
    current_user_role_id = 2  # Temporary. Needs to be fixed
    form = SurveyGroupMemberAddForm(request.form)
    survey_group_members_list = db.session.query(User).add_columns(User.id, User.email).filter(
        User.role_id > current_user_role_id) \
        .order_by(User.email)
    survey_group_members_selection_list = []
    for survey_group_member in survey_group_members_list:
        survey_group_members_selection_list.append((str(survey_group_member.id), survey_group_member.email))
    form.member_id.choices = survey_group_members_selection_list
    if request.method == 'POST' and form.validate():
        for member_id in form.member_id.data:
            survey_group_member = SurveyGroupMember(survey_group_id, member_id)
            db.session.add(survey_group_member)
            db.session.commit()
        # Success. Redirect user to full survey group list.
        return redirect(url_for('home'))
    # Load the page. If page was submitted and contain errors then load it with errors.
    return render_template('pages/survey-group-member-add.html', form=form)


@app.route('/survey/group/<int:survey_group_id>/member/list')
def survey_group_member_list(survey_group_id):
    current_user_id = 2  # Temporary. Needs to be fixed
    subquery = db.session.query(SurveyGroupMember).add_column(SurveyGroupMember.member_id).filter(
        SurveyGroupMember.survey_group_id == survey_group_id).subquery()
    survey_group_member_list = db.session.query(User).filter(User.id == subquery.c.member_id).order_by(User.email)
    return render_template('pages/survey-group-member-list.html', survey_group_member_list=survey_group_member_list)


@app.route('/survey/add', methods=['GET', 'POST'])
def survey_add():
    """ Provide HTML form to create new survey """
    current_user_id = 2  # Temporary. Needs to be fixed
    form = SurveyAddForm(request.form)
    survey_group_list = db.session.query(SurveyGroup).add_columns(SurveyGroup.id, SurveyGroup.name) \
        .filter(SurveyGroup.creator_id == current_user_id)
    survey_group_selection_list = []
    for survey_group in survey_group_list:
        survey_group_selection_list.append((str(survey_group.id), survey_group.name))
    form.survey_group_id.choices = survey_group_selection_list
    if request.method == 'POST' and form.validate():
        new_survey = Survey()
        form.populate_obj(new_survey)
        new_survey.creator_id = current_user_id
        db.session.add(new_survey)
        db.session.commit()
        # Success. Redirect user to full survey group list.
        return redirect(url_for('home'))
    # Load the page. If page was submitted and contain errors then load it with errors.
    return render_template('pages/survey-add.html', form=form)


@app.route('/survey/list')
def survey_list():
    current_user_id = 2  # Temporary. Needs to be fixed
    survey_list = db.session.query(Survey).filter(Survey.creator_id == current_user_id)
    return render_template('pages/survey-list.html', survey_list=survey_list)


@app.route('/survey/<int:survey_id>', methods=['GET', 'POST'])
def survey(survey_id):
    """ Provide HTML form to create new survey """
    current_user_id = 2  # Temporary. Needs to be fixed
    form = SurveyForm(request.form)
    survey_data = db.session.query(Survey).filter(Survey.id == survey_id).all()[0]
    if request.method == 'POST' and form.validate():
        new_survey_data = SurveyData(form.answer.data, survey_id, current_user_id)
        db.session.add(new_survey_data)
        db.session.commit()
        # Success. Redirect user to full survey group list.
        return redirect(url_for('home'))
    # Load the page. If page was submitted and contain errors then load it with errors.
    return render_template('pages/survey.html', form=form, survey_data=survey_data)

# ----- Launch -----#
if __name__ == '__main__':
    # app.run(debug=True)
    app.run()