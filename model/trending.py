from bs4 import BeautifulSoup
import requests
import pandas as pd
from pytrends.request import TrendReq
import time
import random
import json
from flask import jsonify
from __init__ import app, db
from sqlalchemy.exc import IntegrityError
import re
import ast

class Trending(db.Model):
    __tablename__ = 'trendingAnime'
    
    _name = db.Column(db.String(255), unique=False, nullable = False)
    _searches = db.Column(db.Integer, primary_key=True)
    
    
    def __init__(self, name="", searches=0):
        self._name = name
        self._searches = searches
        
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
    
    @property
    def searches(self):
        return self._searches

    @name.setter
    def searches(self, searches):
        self._searches = searches
    
    def __str__(self):
        return json.dumps(self.read())
    
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.remove()
            return None
    def read(self):
        return {
            "name": self.name,
            "searches": self.searches
        }

def initTrending():
    with app.app_context():
        db.create_all()
        names = []
        searche = []
        relevancy = []
        with open('animes.txt','r') as file:
            stringAnime = file.readlines()[0]
            stringAnime = re.sub(r'}{','},{', stringAnime)
            stringAnime = "[" + stringAnime + "]"
            animeList = ast.literal_eval(stringAnime)

            print(animeList)
            data = [entry for entry in animeList if entry["searches"] is not None]

            sorted_data = sorted(data, key=lambda x: x['searches'], reverse=True)           
        for entry in sorted_data:
            names.append(entry['name'])
            searche.append(entry['searches'])
        for i in range(len(names)):
            temp = Trending(name=json.dumps(names[i]), searches=searche[i])
            relevancy.append(temp)
        print(relevancy)
        for i in relevancy:
            i.create()
