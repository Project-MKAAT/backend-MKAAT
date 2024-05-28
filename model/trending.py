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
import os

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
def fetchAnimeTitles():
    animeTitles = []

    urls = [ 'https://myanimelist.net/topanime.php?limit=0' , 'https://myanimelist.net/topanime.php?limit=50' ] 
    for url in urls:
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')

        blockquote_tags = soup.find_all('h3')

        animeTags = [tag.get_text() for tag in blockquote_tags]

        for i in animeTags:
            animeTitles.append(i)
        animeTitles = [item for item in animeTitles if "More" not in item]
    with open('animeTitles.txt', 'a') as file:
        file.write(str(animeTitles))

def getSearches():
    animeRelevancy = []
    with open('animeTitles.txt', 'r') as file:
        lines = file.readlines()
        stringAnime = lines[0]

    listAnime = stringAnime.strip('][').split(', ')
    listAnime = [string.replace("'", "") for string in listAnime]

    def get_weekly_searches(keyword):
        pytrends = TrendReq(hl='en-US', tz=360)
        kw_list = [keyword]

        # Fetch interest over time for the past 7 days
        pytrends.build_payload(kw_list, cat=0, timeframe='now 1-d', geo='', gprop='')
        data = pytrends.interest_over_time()

        # Check if the data is not empty
        if not data.empty:
            data = data.reset_index()
            return data
        else:
            return None

    def summarize_searches(data, keyword):
        if data is not None:
            total_searches = data[keyword].sum()
            return(total_searches)

    print(listAnime)
    while listAnime:
        try:
            for title in listAnime:
                data = get_weekly_searches(title)
                animeRelevancy.append(dict(name=str(title), searches=summarize_searches(data,title)))
                with open('animes.txt', 'a') as file:
                    file.write(str(dict(name=str(title), searches=summarize_searches(data,title))))
                listAnime.remove(title)
                with open('animeTitles.txt', 'w') as file:
                    file.write(str(listAnime))
                print(animeRelevancy)
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 429:
                print("429 again... waiting")
                time.sleep(30)            
            else:
                print("ERROR OTHER THAN HTTP! SHOOT")
                break
            
        except Exception as e:
            print(f"diff error lol: {e}")
            time.sleep(15)
            
def initTrending():
    with app.app_context():
        # fetchAnimeTitles()
        if 1!=1:
            getSearches()
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
