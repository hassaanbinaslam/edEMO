from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class UserRole(Base):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class User(Base):
    """ User of the application """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    role_id = Column(Integer, ForeignKey('user_role.id'))

    def __init__(self, email=None, name=None, bio=None, role_id=None):
        self.email = email
        self.name = name
        self.bio = bio
        self.role_id = role_id

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))


class SurveyGroup(Base):
    __tablename__ = 'survey_group'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, name=None, description=None, creator_id=None):
        self.name = name
        self.description = description
        self.creator_id = creator_id


class SurveyGroupMember(Base):
    __tablename__ = 'survey_group_member'

    id = Column(Integer, primary_key=True, autoincrement=True)
    survey_group_id = Column(Integer, ForeignKey('survey_group.id'))
    member_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, survey_group_id=None, member_id=None):
        self.survey_group_id = survey_group_id
        self.member_id = member_id

    def __repr__(self):
        return (u'<{self.__class__.__name__}: {self.id}>'.format(self=self))


class Survey(Base):
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


class SurveyData(Base):
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
    print("Test Models")
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
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

    users = session.query(User).all()
    print users
    for user in users:
        print "ID: %s, Email: %s, Bio: %s" % (user.id, user.email, user.bio)

    subq = session.query(SurveyGroupMember).add_column(SurveyGroupMember.member_id).filter(
        SurveyGroupMember.survey_group_id == 1).subquery()
    print subq
    # p = session.query(User, SurveyGroupMember).filter(User.id == SurveyGroupMember.member_id).all()
    p = session.query(User).filter(User.id == subq.c.member_id).all()
    print p
    # q = session.query(User).add_columns(User.email, User.name).filter(User.id.in_(p)).all()
    # print q