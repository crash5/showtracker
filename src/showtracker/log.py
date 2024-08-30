import logging
from logging.handlers import RotatingFileHandler


def init_app(app):
    lf = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(message)s [logger=%(name)s process_id=%(process)d file=%(filename)s line=%(lineno)d]"
    )

    file_handler = RotatingFileHandler("app.log", maxBytes=1024 * 1024, backupCount=10)
    file_handler.setFormatter(lf)
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
