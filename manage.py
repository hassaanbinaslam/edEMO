from app import create_app, db
from flask import render_template
from flask.ext.script import Manager, Server, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from app.models import UserRole, User, SurveyGroup, SurveyGroupMember, Survey, SurveyData
import datetime, random, os, string

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, UserRole=UserRole, User=User, SurveyGroup=SurveyGroup,
                SurveyGroupMember=SurveyGroupMember, Survey=Survey, SurveyData=SurveyData)


manager.add_command('db', MigrateCommand)
manager.add_command("shell", Shell(make_context=make_shell_context))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('errors/500.html'), 500


@manager.command
def db_setup():
    # initial database setup
    if db.session.query(UserRole).count() == 0:
        db.session.add(UserRole(1, "SYSTEM_ADMIN"))
        db.session.add(UserRole(2, "SURVEY_ADMIN"))
        db.session.add(UserRole(3, "SURVEY_TAKER"))


@manager.command
def init_demo():
    staker_email = os.environ.get('DEMO_SURVEY_TAKER_EMAIL') or 'staker@demo.com'
    sadmin_email = os.environ.get('DEMO_SURVEY_ADMIN_EMAIL') or 'sadmin@demo.com'
    staker_pass = os.environ.get('DEMO_SURVEY_TAKER_PASS') or 'staker'
    sadmin_pass = os.environ.get('DEMO_SURVEY_ADMIN_PASS') or 'sadmin'
    dtaker_email = 'dtaker@demo.com'  # temp demo user that could not be logged in
    dtaker_pass = ''.join(random.choice(string.ascii_uppercase) for i in range(5))  # random string

    # remove all previous demo data
    staker = User.query.filter_by(email=staker_email).first()
    dtaker = User.query.filter_by(email=dtaker_email).first()
    sadmin = User.query.filter_by(email=sadmin_email).first()

    if staker:
        User.query.filter_by(id=staker.id).delete()
        SurveyData.query.filter_by(user_id=staker.id).delete()
        SurveyGroupMember.query.filter_by(email=staker_email).delete()
    if dtaker:
        User.query.filter_by(id=dtaker.id).delete()
        SurveyData.query.filter_by(user_id=dtaker.id).delete()
    if sadmin:
        User.query.filter_by(id=sadmin.id).delete()
        Survey.query.filter_by(creator_id=sadmin.id).delete()
        SurveyGroup.query.filter_by(creator_id=sadmin.id).delete()

    # add a new user = Survey Taker
    dtaker = User()
    dtaker.email = dtaker_email
    dtaker.name = 'Demo Survey Taker'
    dtaker.role_id = 3
    dtaker.set_password(dtaker_pass)
    dtaker.confirmed = False
    db.session.add(dtaker)
    dtaker_id = User.query.filter_by(email=dtaker_email).first().id

    # Add a new user = Survey Admin
    sadmin = User()
    sadmin.email = sadmin_email
    sadmin.name = 'Demo Survey Admin'
    sadmin.role_id = 2
    sadmin.set_password(sadmin_pass)
    sadmin.confirmed = True
    db.session.add(sadmin)
    sadmin_id = User.query.filter_by(email=sadmin_email).first().id


    # Create demo survey groups for survey admin
    db.session.add(SurveyGroup('Class A', 'Demo Class A', sadmin_id))
    db.session.add(SurveyGroup('Class B', 'Demo Class B', sadmin_id))
    sgroup_id_a = SurveyGroup.query.filter_by(name='Class A').first().id
    sgroup_id_b = SurveyGroup.query.filter_by(name='Class B').first().id

    # Create demo surveys for survey admin
    # 4 for 'Class A' and 6 for 'Class B'

    # for class A
    for a in range(4):
        title = 'Class A: Week ' + str(a + 1)
        question = 'This is a demo survey. Choose any answer.'
        db.session.add(
            Survey(title, question, datetime.date.today(), datetime.date.today() + datetime.timedelta(days=2), sadmin_id, sgroup_id_a))

    # for class B
    for a in range(6):
        title = 'Class B: Week ' + str(a + 1)
        question = 'This is a demo survey. Choose any answer.'
        db.session.add(
            Survey(title, question, datetime.date.today(), datetime.date.today() + datetime.timedelta(days=2), sadmin_id, sgroup_id_b))


    # insert surveys data
    # logic: for each survey group get a list of survey ids. for each survey randomly choose answer between 1-5, 10 times

    # for class A
    surveys = Survey.query.filter(Survey.survey_group_id == sgroup_id_a).all()
    for survey in surveys:
        for a in range(10):
            db.session.add(SurveyData(random.randint(1, 5), survey.id, dtaker_id))

    # for class B
    surveys = Survey.query.filter(Survey.survey_group_id == sgroup_id_b).all()
    for survey in surveys:
        for a in range(10):
            db.session.add(SurveyData(random.randint(1, 5), survey.id, dtaker_id))

    # create a user for demo survey taker
    staker = User()
    staker.email = staker_email
    staker.name = 'Demo Survey Taker'
    staker.role_id = 3
    staker.set_password(staker_pass)
    staker.confirmed = True
    db.session.add(staker)
    staker_id = User.query.filter_by(email=staker_email).first().id

    # add survey taker to demo survey groups A
    db.session.add(SurveyGroupMember(sgroup_id_a, staker_email))


if __name__ == '__main__':
    manager.run(default_command='runserver')