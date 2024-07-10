import os
import re
import sys
import textwrap
from pathlib import Path

from ruamel.yaml import YAML
from easydict import EasyDict as edict
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", backtrace=False, diagnose=False,
           format="\r<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {message}")

yaml = YAML()


class Config:

    def __init__(self, config_file: Path):
        self._file = config_file
        self._raw = {}
        self.token = None
        self.admin = None
        self.database = None
        self.i18n = None
        self._load()

    def _load(self):
        if self._file.is_file():
            _raw = yaml.load(self._file)
            if not _raw:
                logger.error(f"Error while loading '{self._file}': File is empty")
                logger.warning("Removing it...")
                os.remove(self._file)
                return self._load()
            if not isinstance(_raw, dict):
                logger.error(f"Error while loading '{self._file}': Bad file-type. Remove it or fix.")
                exit(1)
            self._raw = edict(_raw)
            self.token = self._raw.telegram.token
            self.admin = self._raw.telegram.admin
            self.database = self._raw.database
            self.i18n = self._raw.i18n
            self.i18n.yaml = yaml
            if not re.match(r"[0-9]{1,}:[a-zA-Z0-9_-]{35}", self.token):
                logger.error("Error while loading: Bad telegram token.")
                exit(1)
            logger.success("Configuration loaded.")
        else:
            logger.info("Generating new config file..")
            with open(self._file, "w", encoding="utf-8") as f:
                f.write(textwrap.dedent("""\
                    telegram:
                      token: BOT_TOKEN_HERE  # Bot token
                      admin: ADMIN_ID  # tg_id of admin user
                    
                    database:
                      type: SQLITE  # SQLITE; MYSQL; PGSQL
                      file: data.db
                    
                    i18n:
                      dir: translates  # Directory for i18n
                      default: auto  # Default language
                    """))
            logger.success(f"Config file generated. File: '{self._file}'")
            exit(1)
