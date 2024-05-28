from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource
from datetime import datetime
import jwt
from auth_middleware import token_required
from model.trending import Trending  # Import the Message class
from __init__ import app, db

trending_api = Blueprint("trending_api", __name__, url_prefix="/api/trending/")

api = Api(trending_api)

class TrendingAPI:
    class _CRUD(Resource):
        
        def get(self):  # Read Method
            animes = Trending.query.all()  # read/extract all users from database
            json_ready = [anime.read() for anime in animes]  # prepare output in json
            return jsonify(
                json_ready
            )



api.add_resource(TrendingAPI._CRUD, "/")
