import unittest
import os
import shutil
import json
from urlparse import urlparse
from StringIO import StringIO

import sys; print sys.modules.keys()
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def test_songs_get(self):
        """get all the songs in a database..."""
        fileR = models.File(name="red_song.mp3")
        fileB = models.File(name="blue_song.mp3")
        songR = models.Song(file=fileR)
        songB = models.Song(file=fileB)
        session.add_all([fileR, fileB, songR, songB])
        session.commit()

        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)

        self.assertEqual(data[0]["file"]["id"], fileR.id)
        self.assertEqual(urlparse(data[0]["file"]["path"]).path,"/uploads/red_song.mp3")

        self.assertEqual(data[1]["file"]["id"], fileB.id)
        self.assertEqual(urlparse(data[1]["file"]["path"]).path,"/uploads/blue_song.mp3")
        
    def test_song_post(self):
        """ Add a new song """        
        file = models.File(name="green_song.mp3")
        session.add(file)
        session.commit()

        data = {
            "file": {
                "id": file.id
            }
        }
        
        response = self.client.post("/api/songs",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)
        
        song = songs[0]
        self.assertEqual(song.file.id, file.id)

        data = json.loads(response.data)
        self.assertEqual(data["file"]["id"], file.id)
        self.assertEqual(urlparse(data["file"]["path"]).path, "/uploads/green_song.mp3")
        
    def test_song_delete(self):
        """deleting songs from database"""
        #create database
        fileP = models.File(name="purple_song.mp3")
        fileO = models.File(name="orange_song.mp3")
        fileG = models.File(name="green_song.mp3")
        songP = models.Song(file=fileP)
        songO = models.Song(file=fileO)
        songG = models.Song(file=fileG)        
        session.add_all([songP, songO, songG, fileP, fileO, fileG])
        session.commit()
        
        response = self.client.delete("/api/songs/3",
            headers=[("Accept", "application/json")]
        )
                       
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
                              
        songA = data[0]
        self.assertEqual(songA["file"]["name"], "purple_song.mp3")
                
        songB = data[1]
        self.assertEqual(songB["file"]["name"], "orange_song.mp3")
    
    def test_song_edit(self):
        """edit song from database"""
        #create populate database
        fileR = models.File(name="red_song.mp3")
        fileG = models.File(name="blue_song.mp3")
        fileB = models.File(name="green_song.mp3")
        songR = models.Song(file=fileR)
        songG = models.Song(file=fileG)
        songB = models.Song(file=fileB)        
        session.add_all([songR, songG, songB, fileR, fileG, fileB])
        session.commit()
        
        data = {
            "name": "brown_song.mp3"
        }
        
        response = self.client.put("/api/songs/{}".format(songB.id),
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )
                       
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data["file"]["name"], "brown_song.mp3")

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 3)
                              
        songB = songs[2]
        self.assertEqual(songB.file.name, "brown_song.mp3")
        
    def test_get_uploaded_file(self):
        """testing that we get uploaded files"""
        path =  upload_path("test.txt")
        with open(path, "w") as f:
            f.write("File contents")

        response = self.client.get("/uploads/test.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(response.data, "File contents")
    
    def test_file_upload(self):
        """testing that files upload correctly"""
        data = {
            "file": (StringIO("File contents"), "test.txt")
        }

        response = self.client.post("/api/files",
            data=data,
            content_type="multipart/form-data",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(urlparse(data["path"]).path, "/uploads/test.txt")

        path = upload_path("test.txt")
        self.assertTrue(os.path.isfile(path))
        with open(path) as f:
            contents = f.read()
        self.assertEqual(contents, "File contents")
      
    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())