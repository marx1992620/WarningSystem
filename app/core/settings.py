import logging
import logging.config
import copy
import inspect
import json
import os
import sys
import secrets
import socket
from datetime import datetime
from confluent_kafka import Producer


current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
root_dir = os.path.abspath(os.sep)

class AppSettings:

    VERSION = '1.0'
    # Debug mode
    DEBUG = False

    DATA_DIR = os.path.join(current_dir, "dst")
    SETTING_DIR = os.path.join(DATA_DIR, "setting")
    STATION_INFO_DIR = os.path.join(DATA_DIR, "station_info.json")
    TMP_DIR = os.path.join(current_dir, "tmp")
    TEMPLATE_FILE_DIR = os.path.join(current_dir, "templates")

    # UI config
    UI_IP = "172.28.146.46" #"172.22.248.174" 蘇州172.22.249.48 , 172.28.146.46:6090,8013
    UI_PORT = 8081 #8090

    # Django config
    Django_IP =  "172.28.146.46" #"172.28.146.46"
    Django_PORT = 8013 #8013

    UPLOAD_REQUEST_TIMEOUT = 5
    QUERY_REQUEST_TIMEOUT = 5

    # Kafka broker
    KAFKA_BROKER = "172.28.146.46:9093"

    # Warning server port
    WARNING_PORT = 8077

    # Logging config
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "infoFormat": {
                "format": "%(asctime)s - %(levelname)s - %(module)s: %(message)s",
                "datefmt": "%m/%d/%Y %H:%M:%S %p"
            },
            "errorFormat": {
                "format": "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d: %(message)s"
            }

        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "infoFormat"
            },
            "info": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "infoFormat",
                "mode": "a",
                "filename": os.path.join(DATA_DIR, "logs", "info.log"),
                "maxBytes": 10485760,
                "backupCount": 5,
                "encoding": "utf8"
            },
            "error": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "errorFormat",
                "mode": "a",
                "filename": os.path.join(DATA_DIR, "logs", "error.log"),
                "maxBytes": 10485760,
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "debug": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False
            },
            "gmqtt": {
                "level": "ERROR"
            }
        },

        "root": {
            "level": "INFO",
            "handlers": ["console", "info", "error"]
        }
    }

    @classmethod
    def configuration(cls) -> None:
        if not os.path.exists(cls.DATA_DIR):
            os.makedirs(cls.DATA_DIR)

        if not os.path.exists(cls.TMP_DIR):
            os.makedirs(cls.TMP_DIR)

        cls.configure_logging(cls.DATA_DIR)

    @classmethod
    def configure_logging(cls, logDir: str) -> None:
        """

        """
        if not os.path.exists(os.path.join(logDir, "logs")):
            os.mkdir(os.path.join(logDir, "logs"))

        logging.config.dictConfig(cls.LOGGING)

    @classmethod
    def load_configuration(cls, config: dict) -> None:
        for key, value in config.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
            else:
                logging.error(
                    f"Invaild attribute {key}. Please check your config file.")
                raise ValueError(
                    f"Invaild attribute {key}. Please check your config file.")

    @classmethod
    def to_dict(cls):
        output = {}
        skip = []

        for member, value in inspect.getmembers(cls):
            if not member.startswith("_") and not inspect.ismethod(value) and member not in skip:
                if not isinstance(value, dict):
                    output[member] = value
                else:
                    output[member] = copy.deepcopy(value)
        return output

    @classmethod
    def update_flag(cls):
        cls.FLAG = secrets.token_urlsafe(16)
    
    @classmethod
    def set_warning_port(cls, port=8085, max_port=65535):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while port <= max_port:
            try:
                sock.bind(('', port))
                sock.close()
                logging.info(f"WarningSystem will bind port: {port}")
                AppSettings.WARNING_PORT = port

                return AppSettings.WARNING_PORT
            except OSError:
                port += 1
        raise IOError('no free ports') 


class Warning:
    product: str = None
    project: str = None
    factory: str = None
    floor: str = None
    line: str = None
    cell_type: str = None
    cell_id: str = None
    ip: str = None
    mac_address: str = None
    registered_status: bool = False
    update_time: datetime = None
    connect_to_django: bool = False
    connect_to_ui: bool = False
    update_overlay_status: str = ""
    daemon_status: str = "Initial status"
    connection: bool = False


    @classmethod
    def update_producer(cls):
        cls.__producer = Producer({
        "bootstrap.servers":AppSettings.KAFKA_BROKER,
    })

    @classmethod
    def save_config(cls):
        config_dir = os.path.join(AppSettings.STATION_INFO_DIR)
        with open(config_dir, "w") as f:
            f.write(json.dumps(cls.to_dict(), indent=4, default=str))

    @classmethod
    def remove_register_info(cls):
        Warning.product = None
        Warning.project = None
        Warning.factory = None
        Warning.floor = None
        Warning.line = None
        Warning.cell_type = None
        Warning.cell_id = None
        Warning.update_time = None
        Warning.registered_status = False

    @classmethod
    def get_config(cls):
        return {
            "product": cls.product,
            "project": cls.project,
            "factory": cls.factory,
            "floor": cls.floor,
            "line": cls.line,
            "cell_type": cls.cell_type,
            "cell_id": cls.cell_id,
            "ip": cls.ip,
            "mac_address": cls.mac_address,
        }

    @classmethod
    def to_dict(cls):
        output = {}
        skip = []

        for member, value in inspect.getmembers(cls):
            if not member.startswith("_") and not inspect.ismethod(value) and member not in skip:
                if not isinstance(value, dict):
                    output[member] = value
                else:
                    output[member] = copy.deepcopy(value)
        return output
