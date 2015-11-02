import os
from app import create_app, db
from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand
from app.models import UserRole, User, SurveyGroup, SurveyGroupMember, Survey, SurveyData
import datetime

app = create_app('default')
manager = Manager(app)
#manager.add_command("runserver", Server())
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db)
manager.add_command('db', MigrateCommand)

@manager.command
def db_setup():
    'Setup db basic data'
    db.session.query(UserRole).delete()
    db.session.query(User).delete()
    if db.session.query(UserRole).count() == 0:
        db.session.add(UserRole(1, "SYSTEM_ADMIN"))
        db.session.add(UserRole(2, "SURVEY_ADMIN"))
        db.session.add(UserRole(3, "SURVEY_TAKER"))
    if db.session.query(User).count() == 0:
        user1 = User("admin@localhost.com", "Admin", "System Admin", 1)
        user1.set_password('cat')
        db.session.add(user1)
    print 'Good'

@manager.command
def db_test():
    #db.session.add(SurveyGroup('First Group', 'test group', '1'))
    #db.session.add(SurveyGroup('Second Group', 'test group', '1'))

    #db.session.add(SurveyGroupMember('1', '2'))
    #db.session.add(SurveyGroupMember('1', '3'))
    q = """Please choose the face which most represents your feelings to the statement: I am confident that I will
    complete the project, and I am following my proposed project timeline."""
    #db.session.add(Survey('First', q, datetime.date.today(), datetime.date.today(), '1', '1'))
    #db.session.add(Survey('Second', 'Q?', datetime.date.today(), datetime.date.today(), '1', '1'))
    db.session.add(SurveyData(1,1,1))

if __name__ == '__main__':
    # db.drop_all()
    # db.init_app(app)
    # db.create_all()
    # manager.run(default_command='runserver')
    # app.run()
    manager.run()
    """
    https://github.com/miguelgrinberg/flasky/issues/18
    1. delete migrations folder
    2. python manage.py db init
    3. python manage.py db migrate
    4. python manage.py db upgrade
    5. python manage.py db_setup
    6. python manage.py runserver
    """