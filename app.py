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
db.session.query(UserRole).delete()
db.session.query(User).delete()
if db.session.query(UserRole).count() == 0:
    db.session.add(UserRole(1, "SYSTEM_ADMIN"))
    db.session.add(UserRole(2, "SURVEY_ADMIN"))
    db.session.add(UserRole(3, "SURVEY_TAKER"))
    db.session.commit()
if db.session.query(User).count() == 0:
    db.session.add(User("admin@localhost", "Admin", "System Admin", 1))
    db.session.commit()

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

# ----- Launch -----#
if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
