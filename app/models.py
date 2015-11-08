from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Date
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from flask import current_app
from . import db, login_manager


class UserRole(db.Model):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def __repr__(self):
        return '<UserRole id:%r , name:%r>' % (self.id, self.name)


class User(UserMixin, db.Model):
    """ User of the application """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    role_id = Column(Integer, ForeignKey('user_role.id'), default=3)
    password = Column(String(255))
    confirmed = Column(Boolean, default=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def generate_confirmation_token(self, expiration=86400):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = generate_password_hash(new_password)
        db.session.add(self)
        return True

    def is_system_admin(self):
        return UserRole.query.filter(UserRole.id == self.role_id).first().name == 'SYSTEM_ADMIN'

    def is_survey_admin(self):
        return UserRole.query.filter(UserRole.id == self.role_id).first().name == 'SURVEY_ADMIN'

    def is_survey_taker(self):
        return UserRole.query.filter(UserRole.id == self.role_id).first().name == 'SURVEY_TAKER'

    def __repr__(self):
        return '<User id:%r , email:%r, name:%r, role_id:%r, confirmed:%r>' % (
        self.id, self.email, self.name, self.role_id, self.confirmed)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class SurveyGroup(db.Model):
    __tablename__ = 'survey_group'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, name=None, description=None, creator_id=None):
        self.name = name
        self.description = description
        self.creator_id = creator_id


class SurveyGroupMember(db.Model):
    __tablename__ = 'survey_group_member'

    id = Column(Integer, primary_key=True, autoincrement=True)
    survey_group_id = Column(Integer, ForeignKey('survey_group.id'))
    email = Column(String(255))

    def __init__(self, survey_group_id=None, email=None):
        self.survey_group_id = survey_group_id
        self.email = email

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))


class Survey(db.Model):
    __tablename__ = 'survey'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    creation_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    creator_id = Column(Integer, ForeignKey('user.id'))
    survey_group_id = Column(Integer, ForeignKey('survey_group.id'))

    def __init__(self, title=None, question=None, creation_date=None, expiry_date=None, creator_id=None,
                 survey_group_id=None):
        self.title = title
        self.question = question
        self.creation_date = creation_date
        self.expiry_date = expiry_date
        self.creator_id = creator_id
        self.survey_group_id = survey_group_id

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))


class SurveyData(db.Model):
    __tablename__ = 'survey_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    answer = Column(String(255), nullable=False)
    survey_id = Column(Integer, ForeignKey('survey.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, answer=None, survey_id=None, user_id=None):
        self.answer = answer
        self.survey_id = survey_id
        self.user_id = user_id

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))

