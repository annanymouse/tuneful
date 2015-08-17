import os
from flask.ext.script import Manager

from getpass import getpass
from werkzeug.security import generate_password_hash
#from tuneful.models import Song, File

from tuneful import app

#from flask.ext.migrate import Migrate, MigrateCommand
from tuneful.database import Base

manager = Manager(app)

class DB(object):
    def __init__(self, metadata):
        self.metadata = metadata

#migrate = Migrate(app, DB(Base.metadata))
#manager.add_command('db', MigrateCommand)

@manager.command
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
    
from tuneful.models import Song, File
from tuneful.database import session

@manager.command
def seed():
    fileR = File(filename="red_song.mp3")
    fileB = File(filename="blue_song.mp3")
    session.add_all([fileR, fileB])

    songR = Song(file=fileR)
    songB = Song(file=fileB)
    session.add_all([songR, songB])
    session.commit()
    
if __name__ == "__main__":
    manager.run()