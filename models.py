from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class UserRole(Base, ):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    def __init__(self, id, name):
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


if __name__ == '__main__':
    print("Test Models")
    engine = create_engine('sqlite:///:memory:', echo=True)
    # engine = create_engine('sqlite:///test.db', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    user1 = User(
        email='1ed@emo',
        name='1edEMO',
        bio='1Hello World')
    user2 = User(
        email='2ed@emo',
        name='2edEMO',
        bio='2Hello World')
    user3 = User(
        email='3ed@emo',
        name='3edEMO',
        bio='3Hello World')
    session.add(user1)
    session.add(user2)
    session.add(user3)
    session.commit()

    users = session.query(User).all()
    for user in users:
        print "ID: %s, Email: %s, Bio: %s" % (user.id, user.email, user.bio)
