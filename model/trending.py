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
from datetime import date
from datetime import datetime, timedelta


class Trending(db.Model):
    __tablename__ = "trendingAnime"

    _name = db.Column(db.String(255), unique=False, nullable=False)
    _searches = db.Column(db.Integer, primary_key=True)
    _genre = db.Column(db.String(255), unique=False, nullable=False)
    _releaseDate = db.Column(db.Date, unique=False, nullable=False)
    _rating = db.Column(db.Float, unique=False, nullable=False)
    _userRating = db.Column(
        db.String(20), default=json.dumps([]), unique=False, nullable=False
    )

    def __init__(
        self,
        name="",
        searches=0,
        genre="",
        releaseDate=date.today(),
        rating=0,
        userRating=json.dumps([]),
    ):
        self._name = name
        self._searches = searches
        self.genre = genre
        self.releaseDate = releaseDate
        self.rating = rating
        self.userRating = userRating

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def searches(self):
        return self._searches

    @searches.setter
    def searches(self, searches):
        self._searches = searches

    @property
    def genre(self):
        return self._genre

    @searches.setter
    def genre(self, genre):
        self._genre = genre

    @property
    def releaseDate(self):
        return self._releaseDate

    @releaseDate.setter
    def releaseDate(self, releaseDate):
        self._releaseDate = releaseDate

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
        # Parse the userRating JSON string and extract the rating values
        user_ratings = json.loads(self._userRating)
        ratings = [list(rating.values())[0] for rating in user_ratings]

        # Calculate the average rating if there are any ratings
        if ratings:
            average_rating = sum(ratings) / len(ratings)
        else:
            average_rating = 0  # Default value when there are no ratings

        return {
            "title": self._name,
            "popularity": self._searches,
            "genre": self._genre,
            "release": self._releaseDate,
            "rating": self._rating,
            "userRating": average_rating,
        }

def generate_random_date(start_year=1985, end_year=2015):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    
    return random_date

def fetchAnimeTitles():
    animeTitles = []

    urls = [
        "https://myanimelist.net/topanime.php?limit=0",
        "https://myanimelist.net/topanime.php?limit=50",
    ]
    for url in urls:
        response = requests.get(url)

        soup = BeautifulSoup(response.content, "html.parser")

        blockquote_tags = soup.find_all("h3")

        animeTags = [tag.get_text() for tag in blockquote_tags]

        for i in animeTags:
            animeTitles.append(i)
        animeTitles = [item for item in animeTitles if "More" not in item]

        animes = animeTitles
        with open("animeTitles.txt", "a") as file:
            file.write(str(animeTitles))

def genreFetch(animeTitles):
    # File to store titles that need manual entries
    manual_entries_file = 'manualEntries.txt'

    # Dictionary to store the results
    animeData = []

    with open(manual_entries_file, 'a') as manual_file:
        for anime in animeTitles:
            try:
                title = anime.replace(' ', '_')
                # URL of the Wikipedia page
                url = f'https://en.wikipedia.org/wiki/{title}'

                # Send a GET request to the URL
                response = requests.get(url)
                
                # Check if the page exists
                if response.status_code == 404:
                    animeData.append({
                        'name': anime,
                        'genre': "N/A",
                        'release_date': generate_random_date() 
                })
                    raise ValueError("Wikipedia page does not exist")

                html_content = response.text

                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find the infobox
                infobox = soup.find('table', {'class': 'infobox'})

                # Handle cases where infobox is not found
                if infobox is None:
                    raise ValueError("Infobox not found")

                # Find the genre row and release date row
                genreRow = infobox.find('th', string='Genre')
                releaseDateRow = infobox.find('th', string='Original run')

                # Handle cases where genre or release date rows are not found
                if genreRow is None or releaseDateRow is None:
                    animeData.append({
                        'name': anime,
                        'genre': "N/A",
                        'release_date': generate_random_date()
                })
                    raise ValueError("Genre or release date row not found")


                # Get the genre information
                genre = genreRow.find_next_sibling('td').get_text().strip()
                cleanedGenre = re.sub(r'\[\d+\]', ', ', genre)
                # Remove the trailing comma and space at the end
                cleanedGenre = cleanedGenre.rstrip(', ')

                # Get the release date information
                releaseDate = releaseDateRow.find_next_sibling('td').get_text().strip()
                releaseDate = releaseDate.split('–')[0].strip()
                releaseDate = datetime.strptime(releaseDate, '%B %d, %Y')

                # Store the results in the dictionary
                animeData.append({
                    'name': anime,
                    'genre': cleanedGenre,
                    'release_date': releaseDate
                })

                # Print the results
                print(f"{anime}: Genre: {cleanedGenre}")
                print(f"{anime}: Release Date: {releaseDate}")

            except Exception as e:
                # Write the title to the manual entries file if there's an error
                with open(manual_entries_file, 'a') as manual_file:
                    manual_file.write(f"{anime}\n")
                print(f"Error processing {anime}: {e}")

    return animeData


        
def getSearches():
    animeRelevancy = []
    with open("animeTitles.txt", "r") as file:
        lines = file.readlines()
        stringAnime = lines[0]

    listAnime = stringAnime.strip("][").split(", ")
    listAnime = [string.replace("'", "") for string in listAnime]

    def get_weekly_searches(keyword):
        pytrends = TrendReq(hl="en-US", tz=360)
        kw_list = [keyword]

        # Fetch interest over time for the past 7 days
        pytrends.build_payload(kw_list, cat=0, timeframe="now 1-d", geo="", gprop="")
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
            return total_searches

    print(listAnime)
    while listAnime:
        try:
            for title in listAnime:
                data = get_weekly_searches(title)
                animeRelevancy.append(
                    dict(name=str(title), searches=summarize_searches(data, title))
                )
                with open("animes.txt", "a") as file:
                    file.write(
                        str(
                            dict(
                                name=str(title),
                                searches=summarize_searches(data, title),
                            )
                        )
                    )
                listAnime.remove(title)
                with open("animeTitles.txt", "w") as file:
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
        if 1 != 1:
            getSearches()
        db.create_all()
        names = []
        searche = []
        relevancy = []
        genres = []
        releaseDates = []
        with open("animes.txt", "r") as file:
            stringAnime = file.readlines()[0]
            print("Animes: ",stringAnime)
            stringAnime = re.sub(r"}{", "},{", stringAnime)
            stringAnime = "[" + stringAnime + "]"
            animeList = ast.literal_eval(stringAnime)
            # print(animeList)
            # genreFetch([entry["name"] for entry in animeList])
            # data = [entry for entry in animeList if entry["searches"] is not None]

            # sorted_data = sorted(data, key=lambda x: x["searches"])
        for entry in animeList:
            names.append(entry["name"])
            searche.append(entry["searches"])
        stuff = genreFetch(names)
        print("cool genre stuff: ",stuff)
        for genre in stuff:
            genres.append(genre['genre'])
            releaseDates.append(genre['release_date'])

        for i in range(len(names)):
            if i < len(genres) and i < len(releaseDates):
                temp = Trending(name=names[i], searches=searche[i], genre=genres[i], releaseDate=releaseDates[i])
                relevancy.append(temp)
            else:
                temp = Trending(name=names[i], searches=searche[i])
                relevancy.append(temp)
        for i in relevancy:
            i.create()
    print(len(names))
    print(len(searche))
    print(len(genres))
    print(len(releaseDates))
    print(len(relevancy))