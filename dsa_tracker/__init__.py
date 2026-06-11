import os

from flask import Flask

from .models import db

from flask_login import LoginManager
def create_app(test_config=None):
    database_url = os.environ.get("DATABASE_URL", "sqlite:///dsa_tracker.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-before-deploying"),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "main.login"
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))



    from .routes import main

    app.register_blueprint(main)

    with app.app_context():
        db.create_all()
        from .seed import seed_curriculum

        seed_curriculum()

    return app
