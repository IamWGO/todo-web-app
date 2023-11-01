from html import unescape
from flask import Flask, jsonify, send_from_directory, render_template, request, redirect, url_for, flash
import requests
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import InputRequired, DataRequired, Length
from werkzeug.utils import escape

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

import config

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
jwt = JWTManager(app)


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["GET","POST"])
def login():
    access_token = create_access_token(identity=config.JWT_SECRET_KEY)
    return jsonify(access_token=access_token)


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/delete", methods=["GET"])
def delete():
    auth_result = authorized_request()
    if (auth_result == 200):
        return "delete"
    else:
        return "authorized failed"
    
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# ---Error Handler----
def page_404(e):
    return render_template("errors/404.html")

def page_405(e):
    return render_template("errors/405.html")

def page_401(e):
    return render_template("errors/401.html")

app.register_error_handler(404, page_404)
app.register_error_handler(405, page_405)
app.register_error_handler(401, page_401)


def authorized_request():
    # Create the 'Authorization' header with the JWT token
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY5ODgyNzQ0NCwianRpIjoiNzAzYjM5YmUtZmJiOS00N2M0LWI1YjEtNjZkNWJhYzQ4MWUzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IldBTEVFUkFUOlNJUkFKOk5VUkhBTiIsIm5iZiI6MTY5ODgyNzQ0NCwiZXhwIjoxNjk4ODI4MzQ0fQ.wsUsKT7lxu-1RYDdwUeXpUUJuXyefWrgyCkZru3xB68"
    headers = {
        'Authorization': f"Bearer {jwt_token}"
    }

    # Make an HTTP GET request to the API with the 'Authorization' header
    request_url = request.url_root + "/protected"
    response = requests.get(request_url, headers=headers)
    return response.status_code