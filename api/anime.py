from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource
from datetime import datetime
import jwt
from auth_middleware import token_required
from model.animes import Anime  # Import the Message class
from __init__ import app, db

anime_api = Blueprint("anime_api", __name__, url_prefix="/api/anime/")

api = Api(anime_api)


# helper function for quicksort
def partition(arr, criteria, low, high):
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j][criteria] <= pivot[criteria]:
            i = i + 1
            (arr[i][criteria], arr[j][criteria]) = (arr[j][criteria], arr[i][criteria])

    (arr[i + 1][criteria], arr[high][criteria]) = (
        arr[high][criteria],
        arr[i + 1][criteria],
    )
    return i + 1


# quick sort algorithm
def quickSort(arr, isReversed, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quickSort(arr, low, pi - 1)
        quickSort(arr, pi + 1, high)

    if isReversed:
        arr.reverse()

    return arr


class AnimeAPI:
    class _CRUD(Resource):
        # POST http://127.0.0.1:8069/api/anime/
        @token_required
        def post(self, _):
            # TODO #6
            # body = request.get_json()  # get request

            # # user rating and the title
            # rating = int(body.get("rating"))
            # title = body.get("title")

            # # data checking
            # if not body and not title:
            #     return {"rating": "Content is missing"}, 400

            # userRating = Anime(title=title, userRating=rating)

            try:
                raise NotImplementedError
                # userRating = Anime(title="Tales of Aryan", userRating="2")

                # userRating.update_rating(title="Tales of Aryan", userRating="2")

                # # newRating = userRating.create()
                # # return jsonify(newRating.read()), 201
            except Exception as e:
                return {"rating": f"Failed to create rating: {str(e)}"}, 500

        # GET http://127.0.0.1:8069/api/anime/
        @token_required
        def get(self, _):  # Read Method
            shows = Anime.query.all()
            json_ready = [show.read() for show in shows]
            return jsonify(json_ready)

    class _GetSorted(Resource):
        # POST http://127.0.0.1:8069/api/anime/getsorted
        @token_required
        def post(self):
            body = request.get_json()  # get request

            # get critera
            criteria = body.get("criteria")
            isReversed = eval(body.get("isReversed"))

            messages = Anime.query.all()
            json_ready = [message.read() for message in messages]

            # sort by critera
            json_ready = quickSort(json_ready, criteria, isReversed)
            return jsonify(json_ready)


api.add_resource(AnimeAPI._CRUD, "/")
api.add_resource(AnimeAPI._GetSorted, "/getsorted")
