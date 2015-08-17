# 08-15-2015
# I think this file is in a good place...
import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

import models
import decorators
from tuneful import app
from database import session
from utils import upload_path

@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """ Get a list of songs """
    # Get and filter the songs from the database
    songs = session.query(models.Song)
    songs = songs.all()

    # Convert the posts to JSON and return a response
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")

@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_post():
    data = request.json
    file = session.query(models.File).get(data["file"]["id"])
    if not file:
        data = {"message": "Could not find file with id {}".format(id)}
        return Response(json.dumps(data), 404, mimetype="application/json")

    song = models.Song(file=file)
    session.add(song)
    session.commit()

    data = song.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")
