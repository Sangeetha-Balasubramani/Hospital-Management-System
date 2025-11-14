from sqlalchemy import Date, Time
from datetime import date,time
from .database import db 

class User(db.Model):
    __tablename__='Users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,unique=True,nullable=False)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    contact_number=db.Column(db.String(10),nullable=False)
    dob=db.Column(db.String,nullable=False) 
    gender=db.Column(db.String)
    role=db.Column(db.String,nullable=False,default='patient')
    department_id=db.Column(db.Integer,db.ForeignKey('departments.id'))
    experience=db.Column(db.String,nullable=True)
    status=db.Column(db.Boolean,default=True)
    is_blacklisted=db.Column(db.Boolean,default=False)

    doctor_appointments=db.relationship('Appointment',foreign_keys='Appointment.doctor_id',backref='doctor')
    patient_appointments=db.relationship('Appointment',foreign_keys='Appointment.patient_id',backref='patient')
    patient_treatments=db.relationship('Treatment',foreign_keys='Treatment.patient_id',backref='patient')
    doctor_treatments=db.relationship('Treatment',foreign_keys='Treatment.doctor_id',backref='doctor')


#Department/Specialization
class Department(db.Model):
    __tablename__='departments'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False,unique=True)
    description=db.Column(db.Text,nullable=True)

    doctors=db.relationship('User',backref='department')
    appointments=db.relationship('Appointment',backref='department')

#Appointment
class Appointment(db.Model):
    __tablename__='appointments'
    id=db.Column(db.Integer,primary_key=True)
    patient_id=db.Column(db.Integer,db.ForeignKey('Users.id'),nullable=False)
    doctor_id=db.Column(db.Integer,db.ForeignKey('Users.id'),nullable=False)
    department_id=db.Column(db.Integer,db.ForeignKey('departments.id'),nullable=False)
    date=db.Column(db.String,nullable=False)
    time=db.Column(db.String,nullable=False)
    status=db.Column(db.String,nullable=False)

    treatments=db.relationship('Treatment',backref='appointment')

#Treatment
class Treatment(db.Model):
    __tablename__='treatments'
    id=db.Column(db.Integer,primary_key=True)
    visit_type=db.Column(db.String)
    test_done=db.Column(db.String)
    diagnosis=db.Column(db.String)
    prescription=db.Column(db.String)
    cost=db.Column(db.Float)
    medications=db.Column(db.Text)
    medicines=db.Column(db.String)
    appointment_id=db.Column(db.Integer,db.ForeignKey('appointments.id'),nullable=True)
    patient_id=db.Column(db.Integer,db.ForeignKey('Users.id'),nullable=False)
    doctor_id=db.Column(db.Integer,db.ForeignKey('Users.id'),nullable=True)

#Doctor's_availability
class Doctoravailability(db.Model):
    __tablename__='doctor_availability'
    id=db.Column(db.Integer,primary_key=True)
    doctor_id=db.Column(db.Integer,db.ForeignKey('Users.id'),nullable=False)
    date=db.Column(db.String,nullable=False)
    slot=db.Column(db.String,nullable=False)