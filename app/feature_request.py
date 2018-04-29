from app import app, db
from app.models import User, Request, Client, Area

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Request': Request, 'Client': Client, 'Area': Area}
