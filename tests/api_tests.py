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
        fileR = models.File(filename="red_song.mp3")
        fileB = models.File(filename="blue_song.mp3")
        session.add_all([fileR, fileB])

        songR = models.Song(file=fileR)
        songB = models.Song(file=fileB)
        session.add_all([songR, songB])
        session.commit()

        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)

        self.assertEqual(data[0]["file"]["id"], fileR.id)
        self.assertEqual(urlparse(data[0]["file"]["path"]).path,
                         "/uploads/red_song.mp3")

        self.assertEqual(data[1]["file"]["id"], fileB.id)
        self.assertEqual(urlparse(data[1]["file"]["path"]).path,
                         "/uploads/blue_song.mp3")
        
    def test_song_post(self):
        file = models.File(filename="green_song.mp3")
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

        data = json.loads(response.data)
        self.assertEqual(data["file"]["id"], file.id)
        self.assertEqual(urlparse(data["file"]["path"]).path,
                         "/uploads/green_song.mp3")
        
    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())