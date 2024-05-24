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

        @token_required
        def get(self, _):  # Read Method
            messages = Trending.query.all()
            json_ready = [message.read() for message in messages]
            return jsonify(json_ready)



api.add_resource(TrendingAPI._CRUD, "/")
