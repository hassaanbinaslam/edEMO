from flask import render_template, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user
from . import main
from .forms import SurveyGroupCreationForm, SurveyAddForm, SurveyForm, UserProfileEditForm
from ..models import UserRole, User, SurveyGroup, SurveyGroupMember, Survey, SurveyData
from .. import db
import datetime


@main.route('/')
@login_required
def home():
    if current_user.is_survey_taker():
        # get survey groups in which user is added
        survey_groups = SurveyGroupMember.query.filter(SurveyGroupMember.email == current_user.email).subquery()
        # get surveys user has already taken
        surveys_taken = SurveyData.query.filter(SurveyData.user_id == current_user.id).all()
        # surveys id list taken by current user
        surveys_taken_list = []
        for survey in surveys_taken:
            surveys_taken_list.append(survey.survey_id)

        # get surveys associated with survey groups
        # filter surveys that are expired
        # filter surveys user has already taken
        surveys = Survey.query.filter(Survey.survey_group_id == survey_groups.c.survey_group_id) \
            .filter(Survey.expiry_date >= datetime.date.today()) \
            .filter(Survey.id.notin_(surveys_taken_list)).all()

        return render_template('pages/home_survey_taker.html', surveys=surveys)
    elif current_user.is_survey_admin():
        return render_template('pages/home_survey_admin.html')
    elif current_user.is_system_admin():
        return render_template('pages/home_system_admin.html')
    return render_template('errors/404.html')


@main.route('/profile')
def profile():
    return render_template('pages/view_profile.html')


@main.route('/survey/group/add', methods=['GET', 'POST'])
@login_required
def survey_group_add():
    """ Provide HTML form to create new survey group """

    # this page is limited to SURVEY_ADMIN only. Check if current user is SURVEY_ADMIN
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    form = SurveyGroupCreationForm(request.form)
    if request.method == 'POST' and form.validate():
        validated_mail_lists = form.validate_members_email_list()  # return [good list, bad list]

        # check if there is no invalid email address received from user
        if len(validated_mail_lists[1]) > 0:
            flash(
                "These mail address are not valid and are removed from the list. Please check and submit the form again: "
                + '\n'.join(validated_mail_lists[1]),
                'error')
            form.members.data = ", ".join(validated_mail_lists[0])
            return render_template('pages/survey_group_add.html', form=form)

        survey_group = SurveyGroup()
        form.populate_obj(survey_group)
        survey_group.creator_id = current_user.id
        db.session.add(survey_group)

        survey_group_id = SurveyGroup.query.filter_by(name=survey_group.name).first().id
        for member in validated_mail_lists[0]:
            db.session.add(SurveyGroupMember(survey_group_id, member))

        # Success. Redirect user to full survey group list.
        return redirect(url_for('main.home'))
    # Load the page. If page was submitted and contain errors then load it with errors.
    return render_template('pages/survey_group_add.html', form=form)


@main.route('/survey/group/list')
@login_required
def survey_group_list():
    # this page is limited to SURVEY_ADMIN only. Check if current user is SURVEY_ADMIN
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    survey_groups = db.session.query(SurveyGroup).filter(SurveyGroup.creator_id == current_user.id) \
        .order_by(SurveyGroup.name).all()
    return render_template('pages/survey_group_list.html', survey_group_list=survey_groups)


@main.route('/survey/add', methods=['GET', 'POST'])
@login_required
def survey_add():
    """ Provide HTML form to create new survey """

    # this page is limited to SURVEY_ADMIN only. Check if current user is SURVEY_ADMIN
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    form = SurveyAddForm(request.form)
    survey_group_list = db.session.query(SurveyGroup).filter(SurveyGroup.creator_id == current_user.id) \
        .order_by(SurveyGroup.name).all()

    survey_group_selection_list = []
    for survey_group in survey_group_list:
        survey_group_selection_list.append((str(survey_group.id), survey_group.name))
    form.survey_group_id.choices = survey_group_selection_list

    if request.method == 'POST' and form.validate():
        new_survey = Survey()
        form.populate_obj(new_survey)
        new_survey.creator_id = current_user.id
        db.session.add(new_survey)
        # Success. Redirect user to full survey group list.
        flash("Survey '" + new_survey.title + "' has been created.", 'success')
        return redirect(url_for('main.home'))
    # Load the page. If page was submitted and contain errors then load it with errors.
    return render_template('pages/survey_add.html', form=form, survey_group_list=survey_group_list)


@main.route('/survey/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def survey(survey_id):
    """ Provide HTML form to create new survey """

    # check if requested survey is available in the system
    # also check if survey has not already expired
    requested_survey = db.session.query(Survey).filter(Survey.id == survey_id) \
        .filter(Survey.expiry_date >= Survey.creation_date).first()
    if not requested_survey:
        print 'Survey is not available.'
        return redirect(url_for('main.home'))

    # check if current user is allowed to take the requested survey
    # to do this check if current user is member of the group to which requested survey is assigned
    member = SurveyGroupMember.query.filter(SurveyGroupMember.survey_group_id == requested_survey.survey_group_id) \
        .filter(SurveyGroupMember.email == current_user.email).first()
    if not member:
        print 'Survey is not available to current user.'
        return redirect(url_for('main.home'))

    # check if user has already taken the survey
    survey_already_taken = SurveyData.query.filter(SurveyData.survey_id == survey_id) \
        .filter(SurveyData.user_id == current_user.id).first()
    if survey_already_taken:
        print 'Survey already taken by user.'
        return redirect(url_for('main.home'))

    form = SurveyForm(request.form)
    if request.method == 'POST' and form.validate():
        new_survey_data = SurveyData(form.answer.data, survey_id, current_user.id)
        db.session.add(new_survey_data)

        # Success. Redirect user to full survey group list.
        return redirect(url_for('main.home'))
    # Load the page. If page was submitted and contain errors then load it with errors.
    return render_template('pages/survey.html', form=form, survey_data=requested_survey)


@main.route('/user/role/edit', methods=['GET', 'POST'])
@login_required
def user_role_edit():
    """
    Purpose: From this page system admin users can edit other user roles.
    Permission: This page is available to SYSTEM_ADMIN users only.
    Working:
        a. On request user is first asked to enter the mail address
        b. If provided mail address is not registered in the system then an error message is displayed. Otherwise user
        details are displayed with an option to change the user role.
        c. A success message is displayed to user on change of given user role.
    """

    # check if current user is with system admin role
    if not current_user.is_system_admin():
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        if request.form['btn'] == 'search':
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                role_list = UserRole.query.all()
                return render_template('pages/edit_user_role.html', user=user, role_list=role_list)
            else:
                flash('Entered email address is not registered in the system', 'error')
        elif request.form['btn'] == 'edit':
            user_email = request.form['user_email']
            user_role = request.form['user_role']
            user = User.query.filter_by(email=user_email).first()
            user.role_id = int(user_role)
            db.session.commit()
            flash("User '" + user_email + "' role has been updated", 'success')

    return render_template('pages/edit_user_role.html')


@main.route('/result/list')
@login_required
def result_list():
    # check if current user is survey admin
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    # get a list of surveys
    survey_list = Survey.query.filter_by(creator_id=current_user.id).order_by(Survey.title).all()

    # get list of survey groups
    survey_group_list = SurveyGroup.query.filter_by(creator_id=current_user.id).order_by(SurveyGroup.name).all()

    return render_template('pages/result_list.html', survey_list=survey_list, survey_group_list=survey_group_list)


@main.route('/result/survey/<int:survey_id>')
@login_required
def result_survey(survey_id):
    # this page is only available to survey admin. check if current user is survey admin.
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    # check if current user is the owner of requested survey id
    survey = Survey.query.filter(Survey.id == survey_id and Survey.creator_id == current_user.id).first()
    if not survey:
        return redirect(url_for('main.home'))

    # get survey results
    survey_answers = get_survey_results(survey_id)

    return render_template('pages/result_survey.html', survey=survey, survey_data=survey_answers)


@main.route('/result/survey/group/<int:group_id>')
@login_required
def result_survey_group(group_id):
    # this page is only available to survey admin. check if current user is survey admin.
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    # check if current user is the owner of requested survey group id
    survey_group = SurveyGroup.query.filter(
        SurveyGroup.id == group_id and SurveyGroup.creator_id == current_user.id).first()
    if not survey_group:
        return redirect(url_for('main.home'))

    survey_group_data = {
        'names': [],
        '1': [],
        '2': [],
        '3': [],
        '4': [],
        '5': []
    }

    # get all survey ids that are under requested survey group
    surveys = Survey.query.filter(Survey.survey_group_id == group_id).order_by(Survey.survey_group_id).all()

    for survey in surveys:
        survey_answers = get_survey_results(survey.id)
        survey_group_data.get('names').append(survey.title)
        survey_group_data.get('1').append(survey_answers.get('1'))
        survey_group_data.get('2').append(survey_answers.get('2'))
        survey_group_data.get('3').append(survey_answers.get('3'))
        survey_group_data.get('4').append(survey_answers.get('4'))
        survey_group_data.get('5').append(survey_answers.get('5'))

    return render_template('pages/result_survey_group.html', survey_group=survey_group,
                           survey_group_data=survey_group_data)


@main.route('/survey/list')
@login_required
def survey_list():
    # this page is only available to survey admin. check if current user is survey admin.
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    # get all surveys created by current user
    survey_list = Survey.query.filter_by(creator_id=current_user.id).add_columns(Survey.id, Survey.title).order_by(
        Survey.title).all()

    return render_template('pages/survey_list.html', survey_list=survey_list)


@main.route('/survey/view/<int:survey_id>')
@login_required
def survey_view(survey_id):
    # this page is only available to survey admin. check if current user is survey admin.
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    # check if requested survey exists
    survey = Survey.query.filter_by(id=survey_id).first()
    if not survey:
        return redirect(url_for('main.home'))

    # check if current user is the owner of requested survey
    if not survey.creator_id == current_user.id:
        return redirect(url_for('main.home'))

    return render_template('pages/survey_view.html', survey_data=survey)


@main.route('/survey/edit/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def survey_edit(survey_id):
    # this page is only available to survey admin. check if current user is survey admin.
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    # check if requested survey exists
    survey = Survey.query.filter_by(id=survey_id).first()
    if not survey:
        return redirect(url_for('main.home'))

    # check if current user is the owner of requested survey
    if not survey.creator_id == current_user.id:
        return redirect(url_for('main.home'))

    form = SurveyAddForm(request.form)
    survey_group_data = SurveyGroup.query.filter_by(id=survey.survey_group_id).first()
    form.survey_group_id.choices = [(str(survey_group_data.id), survey_group_data.name)]

    if request.method == 'POST' and form.validate():
        # only survey title, question and expiry date could be changed
        survey.title = form.title.data
        survey.question = form.question.data
        survey.expiry_date = form.expiry_date.data
        db.session.add(survey)
        db.session.commit()
        # Success. Redirect user to home page.
        flash("Survey '" + survey.title + "' has been updated.", 'success')
        return redirect(url_for('main.home'))

    return render_template('pages/survey_edit.html', form=form, survey_data=survey, survey_group_data=survey_group_data)


@main.route('/survey/group/view/<int:group_id>')
@login_required
def survey_group_view(group_id):
    # this page is only available to survey admin. check if current user is survey admin.
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    # check if requested survey group exists
    survey_group = SurveyGroup.query.filter_by(id=group_id).first()
    if not survey_group:
        return redirect(url_for('main.home'))

    # check if current user is the owner of requested survey
    if not survey_group.creator_id == current_user.id:
        return redirect(url_for('main.home'))

    survey_group_members = SurveyGroupMember.query.filter(
        SurveyGroupMember.survey_group_id == survey_group.id).order_by(SurveyGroupMember.email).all()

    survey_group_members_list = []
    for member in survey_group_members:
        survey_group_members_list.append(member.email)

    return render_template('pages/survey_group_view.html', survey_group_data=survey_group,
                           survey_group_members=", ".join(survey_group_members_list))


@main.route('/survey/group/edit/<int:group_id>', methods=['GET', 'POST'])
@login_required
def survey_group_edit(group_id):
    # this page is only available to survey admin. check if current user is survey admin.
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    # check if requested survey group exists
    survey_group = SurveyGroup.query.filter_by(id=group_id).first()
    if not survey_group:
        return redirect(url_for('main.home'))

    # check if current user is the owner of requested survey group
    if not survey_group.creator_id == current_user.id:
        return redirect(url_for('main.home'))

    form = SurveyGroupCreationForm(request.form)

    if request.method == 'POST' and form.validate():
        validated_mail_lists = form.validate_members_email_list()  # return [good list, bad list]

        # check if there is no invalid email address received from user
        if len(validated_mail_lists[1]) > 0:
            flash(
                "These mail address are not valid and are removed from the list. Please check and submit the form again: "
                + '\n'.join(validated_mail_lists[1]),
                'error')
            form.members.data = ", ".join(validated_mail_lists[0])
            return render_template('pages/survey_group_edit.html', form=form)

        survey_group.name = form.name.data
        survey_group.description = form.description.data
        db.session.add(survey_group)

        # delete all previous members attached to survey group
        SurveyGroupMember.query.filter(SurveyGroupMember.survey_group_id == survey_group.id).delete()
        for member in validated_mail_lists[0]:
            db.session.add(SurveyGroupMember(survey_group.id, member))

        # Success. Redirect user to full survey group list.
        flash("Survey group '" + str(survey_group.name) + "' has been updated.", 'success')
        return redirect(url_for('main.home'))

    survey_group_members = SurveyGroupMember.query.filter(SurveyGroupMember.survey_group_id == group_id).all()
    survey_group_members_list = []
    for member in survey_group_members:
        survey_group_members_list.append(member.email)

    return render_template('pages/survey_group_edit.html', form=form, survey_group_data=survey_group,
                           survey_group_members=", ".join(survey_group_members_list))


@main.route('/user/profile')
@login_required
def user_profile():
    return render_template('pages/user_profile.html', user=current_user)


@main.route('/user/profile/edit', methods=['GET', 'POST'])
@login_required
def user_profile_edit():
    form = UserProfileEditForm(request.form)
    if request.method == 'POST' and form.validate():

        current_user.name = form.name.data
        current_user.bio = form.bio.data
        db.session.add(current_user)

        flash('Your profile has been updated.', 'success')
        return redirect(url_for('main.home'))

    return render_template('pages/user_profile_edit.html', user=current_user, form=form)


def get_survey_results(survey_id):
    survey_data = db.session.query(SurveyData.answer, db.func.count(SurveyData.answer)).filter(
        SurveyData.survey_id == survey_id).group_by(SurveyData.answer).order_by(SurveyData.answer).all()

    survey_answers = {
        '1': 0,
        '2': 0,
        '3': 0,
        '4': 0,
        '5': 0
    }

    for data in survey_data:
        survey_answers[data[0]] = data[1]
    return survey_answers