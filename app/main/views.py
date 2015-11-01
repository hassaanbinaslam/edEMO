from flask import render_template, redirect, url_for, request
from . import main
from .forms import UserRegistrationForm, SurveyGroupCreationForm, SurveyGroupMemberAddForm, SurveyAddForm, SurveyForm
from ..models import UserRole, User, SurveyGroup, SurveyGroupMember, Survey, SurveyData
from ..email import send_mail
from .. import db


@main.route('/')
def home():
    return render_template('pages/home.html')

@main.route('/profile')
def profile():
    return render_template('pages/view-profile.html')


@main.route('/user/register', methods=['GET', 'POST'])
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
        # Send confirmation email to user.
        token = new_user.generate_confirmation_token()
        send_mail(new_user.email, 'Confirm Your Account', 'auth/email/confirm', user=new_user, token=token)
        # Success. Redirect user to full users list.
        return redirect(url_for('main.home'))
    # Load the page. If page was submitted and contain errors then load it with errors.
    return render_template('pages/user-register.html', form=form)
    # return render_template('pages/test.html')


@main.route('/survey/group/add', methods=['GET', 'POST'])
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


@main.route('/survey/group/list')
def survey_group_list():
    current_user_id = 2  # Temporary. Needs to be fixed
    survey_group_list = db.session.query(SurveyGroup).filter(SurveyGroup.creator_id == current_user_id)
    return render_template('pages/survey-group-list.html', survey_group_list=survey_group_list)


@main.route('/survey/group/<int:survey_group_id>/member/add', methods=['GET', 'POST'])
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


@main.route('/survey/group/<int:survey_group_id>/member/list')
def survey_group_member_list(survey_group_id):
    current_user_id = 2  # Temporary. Needs to be fixed
    subquery = db.session.query(SurveyGroupMember).add_column(SurveyGroupMember.member_id).filter(
        SurveyGroupMember.survey_group_id == survey_group_id).subquery()
    survey_group_member_list = db.session.query(User).filter(User.id == subquery.c.member_id).order_by(User.email)
    return render_template('pages/survey-group-member-list.html', survey_group_member_list=survey_group_member_list)


@main.route('/survey/add', methods=['GET', 'POST'])
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


@main.route('/survey/list')
def survey_list():
    current_user_id = 2  # Temporary. Needs to be fixed
    survey_list = db.session.query(Survey).filter(Survey.creator_id == current_user_id)
    return render_template('pages/survey-list.html', survey_list=survey_list)


@main.route('/survey/<int:survey_id>', methods=['GET', 'POST'])
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
