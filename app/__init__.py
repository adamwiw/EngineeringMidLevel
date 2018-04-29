from flask import Flask, current_app
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'main.login'
bootstrap = Bootstrap(app)

def create_app():
    with app.test_request_context():
        db.create_all()
    db.session.commit()
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
        
    return app
    
from app import models
