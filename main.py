import threading

# import "packages" from flask
from flask import (
    render_template,
    request,
    send_from_directory,
)  
# import render_template from "public" flask libraries
from flask.cli import AppGroup


# import "packages" from "this" project
from __init__ import app, db, cors


# setup APIs
from api.user import user_api 
from api.anime import anime_api

# database migrations
from model.users import initUsers

# from model.players import initPlayers
from model.animes import initMessages

# Initialize the SQLAlchemy object to work with the Flask app instance
db.init_app(app)

# api register
app.register_blueprint(user_api) 
app.register_blueprint(anime_api)

# catch for URL not found
@app.errorhandler(404) 
def page_not_found(e):
    return render_template("404.html"), 404

# connects default URL to index() function
@app.route("/")  
def index():
    return render_template("index.html")

# connects /stub/ URL to stub() function
@app.route("/table/")  
def table():
    return render_template("table.html")


@app.route("/videos/<path:path>")
def videos(path):
    return send_from_directory("videos", path)


@app.before_request
def before_request():
    # Check if the request came from a specific origin
    allowed_origin = request.headers.get("Origin")
    if allowed_origin in [
        "http://localhost:4100",
        "http://127.0.0.1:4100",
        "https://nighthawkcoders.github.io",
    ]:
        cors._origins = allowed_origin


# Create an AppGroup for custom commands
custom_cli = AppGroup("custom", help="Custom commands")


# Define a command to generate data
@custom_cli.command("generate_data")
def generate_data():
    initUsers()
    initMessages()

# Register the custom command group with the Flask application
app.cli.add_command(custom_cli)

# this runs the application on the development server
if __name__ == "__main__":
    # change name for testing
    app.run(debug=True, host="0.0.0.0", port="8069")
