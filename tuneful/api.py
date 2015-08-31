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
    """get a list of songs """    
    # get all the songs from the database
    songs = session.query(models.Song).all()
    
    # return list of songs...
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")
       
@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_post():
    """add new song..."""
    data = request.json
    file = session.query(models.File).get(data["file"]["id"])
    if not file:
        data = {"message": "There is no file with id {}.".format(id)}
        return Response(json.dumps(data), 404, mimetype="application/json")

    song = models.Song(file=file)
    session.add(song)
    session.commit()

    data = song.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")

@app.route("/api/songs/<int:id>", methods=["DELETE"])
@decorators.accept("application/json")
def song_delete(id):
    """delete song from database"""
    song = session.query(models.Song).get(id)
    file = song.file

    # check if song exists
    if not song:
        message = "There is no song with id {}.".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    session.delete(song)
    session.delete(file)
    session.commit()

    songs = session.query(models.Song).all()

    # return info after deletion
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")
    
@app.route("/api/songs/<int:id>", methods=["PUT"])
@decorators.accept("application/json")
def song_edit(id):
    """ edit an existing song """
    data = request.json
    
    # get file & song from database
    song = session.query(models.Song).get(id)
    file = song.file
    
    # edit the file name in the database
    file.name = data["name"]
    session.commit()

    # setting correct headers for song
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("songs_get")}
    return Response(data, 201, headers=headers, mimetype="application/json")


@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)

@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    """posting a file..."""
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    db_file = models.File(name=filename)
    db_song = models.Song(file=db_file)
    session.add_all([db_file,db_song])    
    session.commit()
    file.save(upload_path(filename))

    data = db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")


#     filename = secure_filename(file.filename)
#     db_file = models.File(name=filename)
#     session.add(db_file)
#     session.commit()
#     file.save(upload_path(filename))

#     data = db_file.as_dictionary()
#     return Response(json.dumps(data), 201, mimetype="application/json")