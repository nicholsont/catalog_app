from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from passlib.apps import custom_app_context as pwd_context
import random
import string


Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))  # noqa


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False)
    email = Column(String, index=True)
    picture = Column(String)

    @property
    def serialize(self):
        """Returns User object data in serializable format"""
        return {
            'name': self.username,
            'id': self.id,
            'email': self.email,
        }

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """Decrypts the token and returns user_id if known"""
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Token has expired
            return None
        except BadSignature:
            # Invalid token
            return None
        user_id = data['id']
        return user_id


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    @property
    def serialize(self):
        """Returns Category object data in serializable format"""
        return {
            'name': self.name,
            'id': self.id
        }


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    picture = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return Item object data in serializable format"""
        return {
            'name': self.name,
            'picture': self.picture,
            'description': self.description
        }


engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
