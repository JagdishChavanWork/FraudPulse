from config.settings import DATABASE_URL
from database.connection import engine


def get_engine():
    return engine
