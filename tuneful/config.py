class DevelopmentConfig(object):
    DATABASE_URI = "postgresql://nitrous:nitrous@localhost:5432/tuneful"
    DEBUG = True
    UPLOAD_FOLDER = "uploads"

class TestingConfig(object):
    DATABASE_URI = "postgresql://nitrous:nitrous@localhost:5432/tuneful-test"
    DEBUG = True
    UPLOAD_FOLDER = "test-uploads"
