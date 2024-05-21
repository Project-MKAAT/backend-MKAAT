from random import randrange
from datetime import date
import os, base64
import json

from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


class Anime(db.Model):
    __tablename__ = "databases"  # table name is plural, class name is singular

    # Define the Message schema with "vars" from object
    _title = db.Column(db.String(255), unique=False, nullable=False)
    _release = db.Column(db.DateTime, nullable=False, default=date.today())
    _genre = db.Column(db.String(255), unique=False, nullable=False)
    _rating = db.Column(db.Integer, nullable=False, default=0)
    _userRating = db.Column(db.Integer, nullable=False, default=0)

    # constructor of a Message object, initializes the instance variables within object (self)
    def __init__(self, title, release, genre, rating, userRating):
        self._title = title
        self._release = release
        self._genre = genre
        self._rating = rating
        self._userRating = userRating

    # a title getter method, extracts title from object
    @property
    def title(self):
        return self._title

    # a setter function, allows title to be updated after initial object creation
    @title.setter
    def is_title(self, title):
        self._title = title

    # a message getter method, extracts message from object
    @property
    def release(self):
        return self._release

    # a setter function, allows release to be updated after initial object creation
    @release.setter
    def release(self, release):
        self._release = release

    # a message getter method, extracts message from object
    @property
    def genre(self):
        return self._genre

    # a setter function, allows genre to be updated after initial object creation
    @genre.setter
    def genre(self, genre):
        self._genre = genre

    # a message getter method, extracts message from object
    @property
    def rating(self):
        return self._rating

    # a setter function, allows rating to be updated after initial object creation
    @rating.setter
    def rating(self, rating):
        self._rating = rating

    # a message getter method, extracts message from object
    @property
    def userRating(self):
        return self._userRating

    # a setter function, allows userRating to be updated after initial object creation
    @userRating.setter
    def userRating(self, userRating):
        self._userRating = userRating

    def create(self):
        try:
            # creates a person object from User(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Users table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.remove()
            return None

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        return {
            "title": self.title,
            "release": self.release,
            "genre": self.genre,
            "rating": self.rating,
            "userRating": self.userRating,
        }

    # CRUD update: updates message content
    # returns self
    def update(self, old_message, new_message):
        message = Anime.query.get(old_message)
        message.message = new_message
        db.session.commit()
        return self

    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


def initMessages():
    with app.app_context():
        """Create database and tables"""
        db.create_all()

        """Tester data for table"""
        a1 = Anime(
            title="Tales of Aryan",
            release="05-20-2024",
            genre="Documentary",
            rating="10.0",
            userRating="10.0",
        )
        animes = [a1]

        """Add message data to the table"""
        for anime in animes:
            try:
                anime.create()
            except IntegrityError:
                """fails with bad or duplicate data"""
                db.session.remove()
                print(f"Records exist, duplicate message, or error: {anime.title}")
