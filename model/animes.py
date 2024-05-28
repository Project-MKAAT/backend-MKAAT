from random import randrange
from datetime import date
import os, base64
import json

from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Anime(db.Model):
    # database name
    __tablename__ = "animes"

    # database fields
    _title = db.Column(db.String(255), primary_key=True, unique=False, nullable=False)
    _release = db.Column(db.DateTime, nullable=False, default=date.today())
    _genre = db.Column(db.String(255), unique=False, nullable=False)
    _rating = db.Column(db.Integer, nullable=False, default=0)
    _userRating = db.Column(db.Integer, nullable=False, default=0)

    # initialize
    def __init__(self, title, release, genre, rating, userRating):
        self._title = title
        self._release = release
        self._genre = genre
        self._rating = rating
        self._userRating = userRating

    # all the getters/setters for each field

    @property
    def title(self):
        return self._title

    @title.setter
    def is_title(self, title):
        self._title = title

    @property
    def release(self):
        return self._release

    @release.setter
    def release(self, release):
        self._release = release

    @property
    def genre(self):
        return self._genre

    @genre.setter
    def genre(self, genre):
        self._genre = genre

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, rating):
        self._rating = rating

    @property
    def userRating(self):
        return self._userRating

    @userRating.setter
    def userRating(self, userRating):
        self._userRating = userRating

    def create(self):
        # adding shows
        try:
            db.session.add(self)
            db.session.commit()
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

    def update_rating(self, newRating):
        self.userRating = newRating
        db.session.commit()
        return self

    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


def initShows():
    with app.app_context():
        """Create database and tables"""
        db.create_all()

        """Tester data for table"""
        a1 = Anime(
            title="Tales of Aryan",
            release=datetime.strptime("5-20-2024", "%m-%d-%Y"),
            genre="Documentary",
            rating=10.0,
            userRating=10.0,
        )
        a2 = Anime(
            title="Aashray Aubstacles",
            release=datetime.strptime("9-13-2002", "%m-%d-%Y"),
            genre="Action",
            rating=6.9,
            userRating=8.8,
        )
        a3 = Anime(
            title="Trevor x Trevor",
            release=datetime.strptime("8-17-2008", "%m-%d-%Y"),
            genre="Action",
            rating=7.2,
            userRating=3.4,
        )

        animes = [a1, a2, a3]

        """Add message data to the table"""
        for anime in animes:
            try:
                anime.create()
            except IntegrityError:
                """fails with bad or duplicate data"""
                db.session.remove()
                print(f"Records exist, duplicate message, or error: {anime.title}")


if __name__ == "__main__":
    initShows()
