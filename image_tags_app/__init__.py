from flask import Flask

# para lanzar en desarrollo
# python -m flask --app __init__ run --debug --port 5000


def create_app():
    app = Flask(__name__)
    
    # existing code omitted
    from . import views
    app.register_blueprint(views.bp)

    return app
