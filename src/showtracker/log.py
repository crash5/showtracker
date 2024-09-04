import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path


def init_app(app):
    lf = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(message)s [logger=%(name)s process_id=%(process)d file=%(filename)s line=%(lineno)d]"
    )

    logpath = Path(app.instance_path)
    logpath.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        logpath / "app.log", maxBytes=1024 * 1024, backupCount=10
    )
    file_handler.setFormatter(lf)
    file_handler.setLevel(logging.DEBUG)

    stream_handler = StreamHandler()
    stream_handler.setLevel(logging.INFO)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    root.addHandler(stream_handler)
