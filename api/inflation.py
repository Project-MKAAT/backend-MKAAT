from flask import Blueprint, request, jsonify, current_app, Response
from flask_restful import Api, Resource # used for REST API building

from model.inflation import InflationModel

inflation_api = Blueprint('inflation_api', __name__,
                   url_prefix='/api/inflation')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(inflation_api)

# Initialize the model
inflation_Model = InflationModel()


class InflationApi:     
    class _CRUD(Resource): 
        def post(self):
            data = request.get_json()
            print(data)
            inflation_rate = inflation_Model.predictInflation(data)
            return jsonify(inflation_rate)

    api.add_resource(_CRUD, '/')