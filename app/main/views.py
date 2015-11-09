from flask import render_template, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user
from . import main
from .forms import SurveyGroupCreationForm, SurveyAddForm, SurveyForm
from ..models import UserRole, User, SurveyGroup, SurveyGroupMember, Survey, SurveyData
from .. import db


@main.route('/')
@login_required
def home():
    if current_user.is_survey_taker():
        # get survey groups in which user is added
        survey_groups = SurveyGroupMember.query.filter(SurveyGroupMember.email == current_user.email).subquery()
        # get surveys user has already taken
        surveys_taken = SurveyData.query.filter(SurveyData.user_id == current_user.id).all()
        surveys_taken_list = []
        for survey in surveys_taken:
            surveys_taken_list.append(survey.survey_id)
        # surveys id list taken by current user
        # print surveys_taken_list

        # get surveys associated with survey groups
        # filter surveys that are expired
        # filter surveys user has already taken
        surveys = Survey.query.filter(Survey.survey_group_id == survey_groups.c.survey_group_id) \
            .filter(Survey.expiry_date >= Survey.creation_date) \
            .filter(Survey.id.notin_(surveys_taken_list)).all()

        return render_template('pages/home_survey_taker.html', surveys=surveys)
    elif current_user.is_survey_admin():
        return render_template('pages/home_survey_admin.html')
    elif current_user.is_system_admin():
        return render_template('pages/home_system_admin.html')
    return render_template('errors/404.html')


@main.route('/profile')
def profile():
    return render_template('pages/view-profile.html')


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
            return render_template('pages/survey-group-add.html', form=form)

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
    return render_template('pages/survey-group-add.html', form=form)


@main.route('/survey/group/list')
@login_required
def survey_group_list():
    # this page is limited to SURVEY_ADMIN only. Check if current user is SURVEY_ADMIN
    if not current_user.is_survey_admin():
        return redirect(url_for('main.home'))

    survey_groups = db.session.query(SurveyGroup).filter(SurveyGroup.creator_id == current_user.id) \
        .order_by(SurveyGroup.name).all()
    print survey_groups
    return render_template('pages/survey-group-list.html', survey_group_list=survey_groups)


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
    return render_template('pages/survey-add.html', form=form, survey_group_list=survey_group_list)


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


@main.route('/edit-user-role', methods=['GET', 'POST'])
@login_required
def edit_role():
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