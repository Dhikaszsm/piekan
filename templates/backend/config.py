class config:
    sqlalchemy_track_modifications = False

class devconfig(config):
    sqlalchemy_database_uri = "postgresql+psycopg2://perikanan:admin@localhost:5432/auth"