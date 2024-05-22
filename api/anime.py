from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource
from datetime import datetime
import jwt
from auth_middleware import token_required
from model.animes import Anime  # Import the Message class
from __init__ import app, db

anime_api = Blueprint("anime_api", __name__, url_prefix="/api/anime/")

api = Api(anime_api)

def partition(arr, criteria, low, high):
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j][criteria] <= pivot[criteria]:
            i = i + 1
            (arr[i][criteria], arr[j][criteria]) = (arr[j][criteria], arr[i][criteria])

    (arr[i + 1][criteria], arr[high][criteria]) = (arr[high][criteria], arr[i + 1][criteria])
    return i + 1

def quickSort(arr, criteria, isReversed, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quickSort(arr, low, pi - 1)
        quickSort(arr, pi + 1, high)

    if isReversed:
        arr.reverse()

    return arr

class AnimeAPI:
    class _CRUD(Resource):
        @token_required
        def post(self, current_user, Anime):
            body = request.get_json() # get request

            # user rating and the title
            rating = int(body.get('rating'))
            title = body.get('title')

            # data checking
            if not body and not title:
                return {"rating": "Content is missing"}, 400

            userRating = Anime(uid=current_user.title, _rating=rating)

            try:
                newRating = userRating.create()
                return jsonify(newRating.read()), 201
            except Exception as e:
                return {"rating": f"Failed to create rating: {str(e)}"}, 500

        @token_required
        def get(self, _):  # Read Method
            messages = Anime.query.all()
            json_ready = [message.read() for message in messages]
            return jsonify(json_ready)

        def put(self, old_message, new_message, likes):
            Anime.update(old_message, new_message, likes)

    class _GetSorted(Resource):
        @token_required
        def post(self, current_user):
            body = request.get_json() # get request

            # get critera
            criteria = body.get('criteria')
            isReversed = eval(body.get('isReversed'))

            messages = Anime.query.all()
            json_ready = [message.read() for message in messages]
            
            # sort by critera
            json_ready = quickSort(json_ready, criteria, isReversed)
            return jsonify(json_ready)
    
    class _Send(Resource):
        def post(self):
            token = request.cookies.get("jwt")
            uid = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )[
                "_uid"
            ]  # current user
            body = request.get_json()
            # Fetch data from the form
            rating = int(body.get('rating'))
            title = body.get('title')
            if uid is not None:
                new_message = Anime(uid=uid, rating=rating, title=title)
            message = new_message.create()
            if message:
                return message.read()
            return {
                "message": f"Processed {uid}, either a format error or User ID {uid} is duplicate"
            }, 400

    class _Likes(Resource):
        def put(self):
            body = request.get_json()
            message = body.get("message")
            message = Anime.query.filter_by(_message=message).first()
            message.likes += 1

    class _Delete(Resource):
        @token_required
        def delete(self, x):  # Delete Method
            body = request.get_json()
            message_id = body.get("message")
            uid = body.get("uid")
            if not message_id:
                return {"message": "Message ID is missing"}, 400

            for message in Message.query.all():
                pass
            if not message:
                return {"message": "Message not found"}, 404

            if message.uid != uid:
                return {"message": "You are not authorized to delete this message"}, 403

            try:
                message.delete()
                return {"message": "Message deleted successfully"}, 200
            except Exception as e:
                return {"message": f"Failed to delete message: {str(e)}"}, 500


api.add_resource(AnimeAPI._CRUD, "/")
api.add_resource(AnimeAPI._Send, "/send")
api.add_resource(AnimeAPI._Delete, "/delete")
api.add_resource(AnimeAPI._Likes, "/like")
api.add_resource(AnimeAPI._GetSorted, "/getsorted")