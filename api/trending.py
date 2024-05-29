from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource
from datetime import datetime
import json, jwt
from auth_middleware import token_required
from model.trending import Trending  # Import the Message class
from __init__ import app, db
from model.trending import Trending, db

trending_api = Blueprint("trending_api", __name__, url_prefix="/api/trending/")

api = Api(trending_api)


class TrendingAPI:
    class _CRUD(Resource):
        def get(self):  # Read Method
            animes = Trending.query.all()  # read/extract all animes from database
            json_ready = [anime.read() for anime in animes]  # prepare output in json
            return jsonify(json_ready)

    class _UserRating(Resource):
        @token_required
        def post(self, current_user):
            body = request.get_json()
            uid = body.get("uid")
            name = body.get("name")
            rating = body.get("rating")
            animes = Trending.query.all()
            for anime in animes:
                if anime.name == name:
                    anime.userRating = json.loads(anime.userRating)
                    print(type(anime.userRating))
                    for user_rating in anime.userRating:
                        if uid in user_rating:
                            return {"message": "You have already rated this show."}, 400
                    anime.userRating.append({uid: rating})
                    anime.userRating = json.dumps(anime.userRating)
                    db.session.commit()
                    return {"message": "Rating added successfully"}, 200
            return {"message": "Anime not found"}, 404


api.add_resource(TrendingAPI._CRUD, "/")
api.add_resource(TrendingAPI._UserRating, "/userRating")
