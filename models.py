"""SQLAlchemy models for AniTrack."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )
    
    password = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


# class Favorite(db.Model):
#     """Storing user's liked animals' ids"""

#     __tablename__ = 'favorites' 

#     id = db.Column(
#         db.Integer,
#         primary_key=True
#     )

#     user_id = db.Column(
#         db.Integer,
#         db.ForeignKey('users.id', ondelete='cascade')
#     )

#     species_name = db.Column(
#         db.Text,
#         nullable=False,
#         unique=True,
#     )


class Animal(db.Model):
    """imported data from the Red List"""

    __tablename__ = 'animals'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    family_name = db.Column(
        db.Text,
        nullable=False
    )

    scientific_name  = db.Column(
        db.Text,
        nullable=False
    )

    main_common_name = db.Column(
        db.Text,
        nullable=True
    )

    category = db.Column(
        db.Text,
        nullable=False
    )

    taxonomicnotes = db.Column(
        db.Text,
        nullable=True
    )

    # # Can get list of contry objects from dept with .contries
    countries = db.relationship('Country',
                               secondary='animals_countries',
                               backref='animal')
    # direct navigation: emp -> employeeproject & back
    # countries = db.relationship('AnimalCountry',
    #                               backref='animal')

    @classmethod
    def update_db(cls, family_name, scientific_name, main_common_name, category):
        """adds an animal to the db
        """

        animal = Animal(
            family_name=family_name,
            scientific_name=scientific_name,
            main_common_name=main_common_name,
            category=category,
            # taxonomicnotes=taxonomicnotes
        )

        db.session.add(animal)
        return animal


    


 


class Country(db.Model):
    """List of countries"""
    # Can get list of animal objects from dept with .animals

    __tablename__ = 'countries'



    country_code = db.Column(
        db.Text,
        primary_key = True
    )

    country_name = db.Column(
        db.Text,
        nullable=False
    )

    animals = db.relationship('Animal',
                               secondary='animals_countries',
                               backref='country')

    @classmethod
    def update_db(cls, country_code, country_name):
        """adds an animal to the db
        """

        country = Country(
            country_code=country_code,
            country_name=country_name,
        )

        db.session.add(country)
        return country




class AnimalCountry(db.Model):
    """RL animals by countries"""


    __tablename__ = 'animals_countries'

    country_code = db.Column(
        db.Text,
        db.ForeignKey('countries.country_code'),
        primary_key=True
    )


    animal_id = db.Column(
        db.Integer,
        db.ForeignKey('animals.id'),
        primary_key=True
    )

    @classmethod
    def update_db(cls, country_code, country_name, species_name):
        """adds an animal to the db
        """

        animal_country = AnimalCountry(
            country_code=country_code,
            country_name=country_name,
            species_name=species_name
        )

        db.session.add(animal_country)
        return animal_country



    
def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)