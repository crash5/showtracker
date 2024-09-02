from flask import Flask
from flask_apscheduler import APScheduler

from . import service, tvmaze


def init_app(app: Flask):
    def update_shows():
        with app.app_context():
            app.logger.info("Update shows from tvmaze.")
            tvmaze.update_shows(service.get_service())

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    scheduler.add_job(
        func=update_shows,
        trigger="interval",
        hours=8,
        id="update_from_tvmaze",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
