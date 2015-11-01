from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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

    '''def __init__(self, email=None, name=None, bio=None, password=None, role_id=None):
        self.email = email
        self.name = name
        self.bio = bio
        self.password = password
        self.role_id = role_id
    '''

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

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))


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
    member_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, survey_group_id=None, member_id=None):
        self.survey_group_id = survey_group_id
        self.member_id = member_id

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


if __name__ == '__main__':
    """
    print("Test Models")
    engine = create_engine('sqlite:///:memory:', echo=True)
    db.Model.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    session.add(UserRole(1, "SYSTEM_ADMIN"))
    session.add(UserRole(2, "SURVEY_ADMIN"))
    session.add(UserRole(3, "SURVEY_TAKER"))
    session.commit()

    session.add(User("admin@localhost", "Admin", "System Admin", 1))
    session.add(User("user1@localhost", "Survey Admin", "Survey Admin", 2))
    session.add(User("user2@localhost", "Survey Taker 1", "Survey Taker 1", 3))
    session.add(User("user3@localhost", "Survey Taker 2", "Survey Taker 2", 3))
    session.commit()

    session.add(SurveyGroup("CS6460", "EdTech", 2))
    session.commit()

    session.add(SurveyGroupMember(1, 3))
    session.add(SurveyGroupMember(1, 4))
    session.add(SurveyGroupMember(1, 3))
    session.add(SurveyGroupMember(1, 4))
    session.commit()

    User.query.all()
        """
    u = User()
    u.set_password('cat')
    print u.password
