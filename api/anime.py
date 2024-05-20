from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource  # used for REST API building

anime_api = Blueprint('anime_api', __name__, url_prefix='/api/anime/')

api = Api(anime_api)

class AnimeApi:
    class _CRUD(Resource):
        def post(self):
            # TODO
            raise NotImplementedError
        
    api.add_resource(_CRUD, "/")
        