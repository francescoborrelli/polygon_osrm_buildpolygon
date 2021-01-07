#  Copyright (c) 2020. AV Connect Inc.
import os
import dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(basedir, '.env'))
import ws_models.config.config as yaml_config

class BC(object):
    @classmethod
    def get_value(cls, key, default_value):
        """ try to get config value first from settings.yaml, then from .env, then from default"""

        # if key in cfg.config():
        #     print("found config key")
        #     return cfg.config()[key]
        # el
        if key in os.environ:
            return os.environ[key]
        else:
            return default_value


class Config(BC):
    FLASK_APP = 'wsgi.py'
    # try:
    #     cfg = yaml_config.Config()
    #
    # except:
    SECRET_KEY = BC.get_value('SECRET_KEY', 'default_secret_key')

    FLASK_ENV = BC.get_value('FLASK_ENV', 'development')

    # SQLALCHEMY_DATABASE_URI = BC.get_value('SQL_URI', 'postgresql://eco_route:crumbaluwadog234@localhost:5432/wsds_test')
    SQLALCHEMY_DATABASE_URI = BC.get_value('SQL_URI', 'sqlite:///../tests/test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    INFLUX_HOST = BC.get_value('INFLUX_HOST', '127.0.0.1')
    INFLUX_PORT = BC.get_value('INFLUX_PORT', '8086')
    INFLUX_DB = BC.get_value('INFLUX_DB', 'telematics')

    REDIS_HOST = BC.get_value('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = BC.get_value('REDIS_PORT', '6379')

    NREL_KEY = BC.get_value('NREL_KEY','7R2V0zMH5WkFTMkUMfUqqPDLRrzMNc5aoIN7DooP')