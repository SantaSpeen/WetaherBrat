import datetime
from pathlib import Path

from loguru import logger


class I18N:
    def __init__(self, _config):
        logger.info("Loading i18n..")
        self._dir = Path(_config.dir)
        self._default = _config.default
        self.yaml = _config.yaml
        self._langs = {}
        self.alias = []
        self._load()

    def _load(self):
        for i in self._dir.walk():
            _, _, filenames = i
            for file in filenames:
                file = self._dir / file
                if file.is_file() and file.suffix == ".yml":
                    data = self.yaml.load(file)
                    self._langs[file.stem] = data
                    self.alias.append([data['_language'], file.stem])
                    logger.success(f"[i18n] {data['_langauge']}({file.stem}) loaded")
            break

    def get(self, phrase, user, **kwargs):
        lang = self._langs.get(user.lang)
        if lang:
            p = lang.get(phrase)
            if isinstance(p, str):
                tz = datetime.timezone(datetime.timedelta(seconds=user.timezone))
                p = p.format(id=user.id, ta=user.alarm_time, tz=tz.tzname(None), **kwargs)
            return p
        return f"unknown phrase: `{phrase}` (`{user.lang}`)"
