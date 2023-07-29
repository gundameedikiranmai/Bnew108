"""
Configuration handler
"""

import sys
import os
from functools import lru_cache
import logging
import logging.config
import yaml
import tomlkit
from pydantic_settings import BaseSettings
from pydantic import Extra
from pymongo import MongoClient


class AppSettings(BaseSettings):
    """
    AppSettings class to allow extra settings values
    """
    class Config:
        extra = Extra.allow

@lru_cache()
def get_app_settings():
    app_env = os.environ.get('ENV','local')
    app_config = os.environ.get('APP_CONFIG','')
    
    config = AppSettings

    with open("config/logging.yml", 'rt',encoding='utf-8') as f:
        log_config = yaml.safe_load(f.read())
        log_config['formatters']['simple']['format'] = log_config['formatters']['simple']['format'].replace("{LOG_PREFIX}",str(os.environ.get('LOG_PREFIX','API')))
        logging.config.dictConfig(log_config)
        logger = logging.getLogger(__name__)
        logger.info("Configured the logger!")
    
    try:
        with open(app_config,'rt',encoding='utf-8') as f:
            config_data = tomlkit.loads(f.read())
    except FileNotFoundError:
        logger.critical('File Not Found at: %s. Verify file and file path in the environment variable',app_config)
        sys.exit(4)

    origins = {"origins": [config_data.get('FRONTEND_DOMAIN')] + config_data.get('FRONTEND_DOMAIN_UI')}
    logger.info('origins: %s', origins)
    os.environ["TZ"] = config_data.get("TIMEZONE")

    uri = f'mongodb://{config_data.get("MONGO_AUTH_USERNAME")}:{config_data.get("MONGO_AUTH_PASSWORD")}@{config_data.get("MONGO_HOSTNAME")}/default_db?authSource={config_data.get("MONGO_AUTH_DATABASE")}'
    mongo = MongoClient(uri)
    db = mongo[config_data.get("MONGO_APP_DATABASE")]

    return config(logger=logger,origins=origins,db=db, **config_data)

settings = get_app_settings()
