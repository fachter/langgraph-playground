import os

from dotenv import load_dotenv

load_dotenv()


class DbConfig:
    USER = os.getenv("DB_USER")
    PASS = os.getenv("DB_PASSWORD")
    HOST = os.getenv("DB_HOST")
    PORT = os.getenv("DB_PORT")
    NAME = os.getenv("DB_NAME")


URL = f"postgresql+psycopg://{DbConfig.USER}:{DbConfig.PASS}@{DbConfig.HOST}:{DbConfig.PORT}/{DbConfig.NAME}"
URL_only_postgres = f"postgresql://{DbConfig.USER}:{DbConfig.PASS}@{DbConfig.HOST}:{DbConfig.PORT}/{DbConfig.NAME}"
URL_params = f"postgresql://{DbConfig.USER}:{DbConfig.PASS}@{DbConfig.HOST}:{DbConfig.PORT}/{DbConfig.NAME}"

connection_string = f"dbname={DbConfig.NAME} host={DbConfig.HOST} user={DbConfig.USER} password={DbConfig.PASS} port={DbConfig.PORT}"

