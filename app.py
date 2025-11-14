from flask import Flask
from application.database import db
app=None

def create_app():
    app= Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///hospital.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False 
    db.init_app(app)
    app.app_context().push()
    return app

app=create_app()
from application.controllers import *

if __name__=='__main__':
    with app.app_context():
        db.create_all()
        admin=User.query.filter_by(role='admin').first()
        if not admin:
            admin=User(username='Admin',email='admin@gmail.com',password='admin123',contact_number='9876543210',dob='23-03-2001',gender='Female',role='admin',status=True)
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)