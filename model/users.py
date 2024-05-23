""" database dependencies to support sqliteDB examples """

from random import randrange
from datetime import date
import os, base64
import json

from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


""" Tutorial: https://www.sqlalchemy.org/library.html#tutorials, try to get into Python shell and follow along """


# Define the User class to manage actions in the 'users' table
# -- Object Relational Mapping (ORM) is the key concept of SQLAlchemy
# -- a.) db.Model is like an inner layer of the onion in ORM
# -- b.) User represents data we want to store, something that is built on db.Model
# -- c.) SQLAlchemy ORM is layer on top of SQLAlchemy Core, then SQLAlchemy engine, SQL
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=False, nullable=False)
    _uid = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column(db.String(255), unique=False, nullable=False)
    _email = db.Column(db.String(255), unique=True, nullable=False)
    _role = db.Column(db.String(20), default="User", nullable=False)
    # Define _preferences as an ARRAY of strings
    _preferences = db.Column(db.String(255), nullable=False)
    _points = db.Column(db.Integer, unique=False)
    _items = db.Column(db.String(255), unique=False, nullable=False)

    # Demo purposes
    #

    # Defines a relationship between User record and Notes table, one-to-many (one user to many notes)
    # posts = db.relationship("Post", cascade="all, delete", backref="users", lazy=True)

    # constructor of a User object, initializes the instance variables within object (self)
    def __init__(
        self,
        name,
        uid,
        email,
        password="123qwerty",
        role="User",
        preferences="none",
        points=0,
        items="[]",
    ):
        self._name = name  # variables with self prefix become part of the object,
        self._uid = uid
        self.set_password(password)
        self._email = email
        self._role = role
        self._preferences = preferences
        self._points = points
        self._items = items

    # a name getter method, extracts name from object
    @property
    def name(self):
        return self._name

    # a setter function, allows name to be updated after initial object creation
    @name.setter
    def name(self, name):
        self._name = name

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        self._items = items

    # a getter method, extracts email from object
    @property
    def uid(self):
        return self._uid

    # a setter function, allows name to be updated after initial object creation
    @uid.setter
    def uid(self, uid):
        self._uid = uid

    # check if uid parameter matches user id in object, return boolean
    def is_uid(self, uid):
        return self._uid == uid

    @property
    def password(self):
        return (
            self._password[0:10] + "..."
        )  # because of security only show 1st characters

    # update password, this is conventional setter
    def set_password(self, password):
        """Create a hashed password."""
        self._password = generate_password_hash(
            password, "pbkdf2:sha256", salt_length=10
        )

    # check password parameter versus stored/encrypted password
    def is_password(self, password):
        """Check against hashed password."""
        result = check_password_hash(self._password, password)
        return result

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    # output content using str(object) in human readable form, uses getter
    # output content using json dumps, this is ready for API response
    def __str__(self):
        return json.dumps(self.read())

    # CRUD create/add a new record to the table
    # returns self or None on error
    def create(self):
        try:
            # creates a person object from User(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Users table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.remove()
            return None

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, role):
        self._role = role

    def is_admin(self):
        return self._role == "Admin"

    # ... (existing code)

    @property
    def preferences(self):
        return self._preferences

    @preferences.setter
    def set_preferences(self, preferences):
        self._preferences = preferences

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        return {
            "id": self.id,
            "name": self.name,
            "uid": self.uid,
            "role": self.role,
            "email": self.email,
            "preferences": self.preferences,
            "points": self.points,
            "items": self.items,
            # "post s": [post.read() for post in self.posts]
        }

    # CRUD update: updates user name, password, phone
    # returns self
    def update(self, name="", uid="", password="", points=0, items=""):
        """only updates values with length"""
        if len(name) > 0:
            self.name = name
        if len(uid) > 0:
            self.uid = uid
        if len(password) > 0:
            self.set_password(password)
        users = User.query.all()
        print(uid)
        for user in users:
            print(uid)
            # print(user.uid)
            if user.uid == uid:
                print(user.items)
                temp = json.loads(user.items)
                temp.append(json.loads(items)[-1])
                sets = set(temp)
                temp2 = []
                for i in sets:
                    temp2.append(i)
                self.items = json.dumps(temp2)
        self.points = points

        db.session.commit()
        return self

    def update_email(self, email=""):
        if len(email) >= 5 and "@" in email:
            self.email = email
        db.session.commit()
        print(self.email)
        return self

    def update_points(self, new_points):
        self.points += new_points
        db.session.commit()
        return self

    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()


"""Database Creation and Testing """


# Builds working data for testing
def initUsers():
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""

        u1 = User(
            name="Aashray Reddy",
            uid="meowZedong",
            email="meowZedong@gmail.com",
            password="password",
            role="Admin",
            points=120,
            items=json.dumps(["adblock"]),
        )
        u2 = User(
            name="Aashray Rajagopalan",
            uid="sigma",
            email="sigma@gmail.com",
            password="password",
            points=100,
            items=json.dumps(["adblock"]),
        )
        u3 = User(
            name="Matthew Wakayama",
            uid="strawberrycreamcheese",
            password="password",
            email="strawberrycreamcheese@gmail.com",
            points=50,
            items=json.dumps(["adblock"]),
        )
        u4 = User(
            name="Trevor Huang",
            uid="黄色的",
            password="password",
            email="黄色的@gmail.com",
            points=400,
            items=json.dumps(["adblock"]),
        )
        u5 = User(
            name="Kyle Liang",
            uid="Kyrle_Riang08-17",
            password="password",
            email="Kyrle_Riang@gmail.com",
            points=400,
            items=json.dumps(["adblock"]),
        )

        users = [u1, u2, u3, u4]
        # print("-------------------------- USERS -----------------------------")
        # print(users)
        """Builds sample user/note(s) data"""
        # i = 0
        for user in users:
            try:
                # print(i)
                # print(user)
                user.create()
            except IntegrityError:
                """fails with bad or duplicate data"""
                db.session.remove()
                print(f"Records exist, duplicate email, or error: {user.uid}")
