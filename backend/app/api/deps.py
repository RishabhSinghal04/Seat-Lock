from functools import cache

from app.core import Config, get_config
from app.services import SMTPMailer

_config: Config = get_config()


@cache
def get_mailer() -> SMTPMailer:
    return SMTPMailer(_config)
