from app import create_app, db
from flask import render_template
from flask.ext.script import Manager, Server, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from app.models import UserRole, User, SurveyGroup, SurveyGroupMember, Survey, SurveyData

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


if __name__ == '__main__':
    manager.run(default_command='runserver')