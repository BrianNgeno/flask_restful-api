from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt()


convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    '''
    user class with attributes; id, username, password
    '''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String,unique=True)
    _password_hash = db.Column(db.String, nullable=False)


    @hybrid_property
    def password_hash(self):
        return self._password_hash
    
    @password_hash.setter
    def password_hash(self,password):
        # Added encoding since this is needed for python3
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')
 

    def authenticate(self,password):
        # Added encoding since this is needed for python3
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
  

class Trainer(db.Model, SerializerMixin):
    '''
    Trainer class with attributes; id, name, bio, specialization, phone_number
    '''
    __tablename__ = 'trainers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,unique=True)
    bio = db.Column(db.String)
    specialization = db.Column(db.String,nullable=True)
    phone_number = db.Column(db.String)
    county = db.Column(db.String)

    sessions = db.relationship('Session', back_populates='trainer')
    trainees = association_proxy('sessions','trainee', creator=lambda thisTrainer: Session(trainer=thisTrainer))
    # __table_args__ = (db.CheckConstraint('len(phone_number)>10'),)
    # manyrelatedobjects = association_proxy('hasmanythroughrelationship','relatedclass', creator= def(thisInstance): AssociationModel(thisRelationship=thisInstance))
    # trainees = association_proxy('sessions','trainee',creator= lambda thisTrainer: Session(trainer = thisTrianer))

    @validates('phone_number')
    def validate_number(self,key,phone_number):
        if len(phone_number)<10:
            raise ValueError("phone number should have length greater than 10")
        return phone_number

class Trainee(db.Model):
    '''
    Trainee class with attributes; id, name, email, phone_number, age
    '''

    __tablename__ = 'trainees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    phone_number = db.Column(db.String)
    age = db.Column(db.Integer)


    sessions = db.relationship('Session', backref='trainee')
    # manyrelatedobjects = association_proxy('hasmanythroughrelationship','relatedclass', creator= def(thisInstance): AssociationModel(thisRelationship=thisInstance))
    trainers = association_proxy('sessions','trainer', creator=lambda thisTrainee: Session(trainee = thisTrainee))

class Session(db.Model):
    '''
    Session class with attributes; id, day, activity, trainer_id, trainee_id
    '''

    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String)
    activity = db.Column(db.String)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'))
    trainee_id = db.Column(db.Integer, db.ForeignKey('trainees.id'))

    trainer = db.relationship('Trainer', back_populates='sessions')


