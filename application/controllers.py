from flask import Flask, render_template, redirect,request,url_for
from flask import current_app as app
from .models import *
from datetime import datetime, timedelta

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        this_user=User.query.filter_by(username=username).first()  
        if this_user:
            if this_user.is_blacklisted:
                return render_template('Blacklist.html',this_user=this_user)
            if this_user.password==password:
                if this_user.role=="admin":
                    return redirect("/admin")
                elif this_user.role=='doctor':
                    return redirect(url_for('doctor_dashboard',doctor_id=this_user.id))
                elif this_user.role=='patient':
                    return redirect(url_for('patients_dashboard',patient_id=this_user.id))
            else:
                return render_template('Incorrect_Password.html')
        else:
            return render_template('Not_Exist.html')
    return render_template('Login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        contact_number=request.form.get("contact_number")
        dob=request.form.get('dob')
        gender=request.form.get('gender')
        role=request.form.get('role')
        user_username=User.query.filter_by(username=username).first()
        user_email=User.query.filter_by(email=email).first()
        if user_username or user_email:
                return render_template('Already.html')
        else:
            user=User(username=username, email=email, password=password, contact_number=contact_number, dob=dob, gender=gender, department_id=None, role=role)
            db.session.add(user)
            db.session.commit()
        return redirect("/login")
    return render_template('Register.html')

##Admin Dashboard
@app.route('/admin',methods=['GET','POST'])
def admin_dashboard():
    this_user=User.query.filter_by(role='admin').first()
    doctors_query=User.query.filter_by(role='doctor')
    patients_query=User.query.filter_by(role='patient')
    departments=Department.query.all()

    search=request.args.get('q','').strip()
    if search:
        if search.isdigit():
            doctors_query=doctors_query.filter(User.id==int(search))
            patients_query=patients_query.filter(User.id==int(search))
        else:
            doctors_query=doctors_query.join(Department,User.department_id==Department.id).filter(
                (User.username.ilike('%'+search+'%'))|
                (Department.name.ilike('%'+search+'%'))
            )
            patients_query=patients_query.filter(User.username.like('%'+search+'%'))

    doctors=doctors_query.all()
    patients=patients_query.all()
    appointments=Appointment.query.all()
    return render_template('Admin_Dashboard.html',this_user=this_user,doctors=doctors,patients=patients,appointments=appointments,departments=departments)

@app.route('/add_doctor',methods=['GET','POST'])
def add_doctor():
    departments=Department.query.all()
    if request.method=='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        contact_number=request.form.get('contact_number')
        dob=request.form.get('dob')
        gender=request.form.get('gender')
        department_id=request.form.get('department_id')
        department_id=int(department_id)
        experience=request.form.get('experience')

        user=User(username=username,email=email,password=password,contact_number=contact_number,dob=dob,gender=gender,role='doctor',department_id=department_id,experience=experience)
        db.session.add(user)
        db.session.commit()
        return redirect("/admin")
    return render_template('Add_Doctor.html',departments=departments)

@app.route('/edit_doctor/<int:doctor_id>',methods=['GET','POST'])
def edit_doctor(doctor_id):
    this_user=User.query.get(doctor_id)

    if request.method=='POST':
        this_user.username=request.form.get('username')
        this_user.contact_number=request.form.get('contact_number')
        this_user.gender=request.form.get('gender')
        this_user.dob=request.form.get('dob')
        this_user.department_name=request.form.get('department_id')
        this_user.experience=request.form.get('experience')
        
        db.session.commit()
        return redirect('/admin')
    return render_template('Edit_Doctor.html',this_user=this_user)

@app.route('/delete_doctor/<int:doctor_id>')
def delete_doctor(doctor_id):        
    this_user=User.query.get(doctor_id)
    db.session.delete(this_user)
    db.session.commit()
    return redirect('/admin')

@app.route('/blacklist_doctor/<int:doctor_id>')
def blacklist_doctor(doctor_id):
    this_user=User.query.get(doctor_id)
    this_user.is_blacklisted=True
    this_user.status=False
    db.session.commit()
    return redirect('/admin')

@app.route('/unblacklist_doctor/<int:doctor_id>')
def unblacklist_doctor(doctor_id):
    this_user=User.query.get(doctor_id)
    if this_user:
        this_user.is_blacklisted=False
        db.session.commit()
    return redirect('/admin')

@app.route('/editpatient_Admin/<int:patient_id>',methods=['GET','POST'])
def editpatient_Admin(patient_id):
    this_user=User.query.get(patient_id)

    if request.method=='POST':
        this_user.username=request.form.get('username')
        this_user.contact_number=request.form.get('contact_number')
        this_user.gender=request.form.get('gender')
        this_user.dob=request.form.get('dob')
        
        db.session.commit()
        return redirect('/admin')
    return render_template('Edit_Patient_Admin.html',this_user=this_user)

@app.route('/delete_patient/<int:patient_id>')
def delete_patient(patient_id):
    this_user=User.query.get(patient_id)
    db.session.delete(this_user)
    db.session.commit()
    return redirect('/admin')

@app.route('/blacklist_patient/<int:patient_id>')
def blacklist_patient(patient_id):
    this_user=User.query.get(patient_id)
    this_user.is_blacklisted=True
    this_user.status=False
    db.session.commit()
    return redirect('/admin')

@app.route('/unblacklist_patient/<int:patient_id>')
def unblacklist_patient(patient_id):
    this_user=User.query.get(patient_id)
    if this_user:
        this_user.is_blacklisted=False
        db.session.commit()
    return redirect('/admin')

@app.route('/patient_history_Admin/<int:patient_id>')
def patient_history_Admin(patient_id):
    this_user=User.query.get(patient_id)
    treatments=Treatment.query.filter_by(patient_id=this_user.id).all()
    for treatment in treatments:
        treatment.doctor=User.query.get(treatment.doctor_id)
    return render_template("Patienthistory_Admin.html",this_user=this_user,patient=this_user,treatments=treatments)

@app.route('/completed_admin/<int:appointment_id>',methods=['GET','POST'])
def completed_admin(appointment_id):
    appointment=Appointment.query.get(appointment_id)
    if appointment:
        appointment.status='completed'
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/cancel_admin/<int:appointment_id>',methods=['GET','POST'])
def cancel_admin(appointment_id):
    appointment=Appointment.query.get(appointment_id)
    if appointment:
        appointment.status='cancelled'
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

    
##Doctor Dashboard
@app.route('/doctor_dashboard/<int:doctor_id>',methods=['GET','POST'])
def doctor_dashboard(doctor_id):
    this_user=User.query.get(doctor_id)
    appointments=Appointment.query.filter_by(doctor_id=this_user.id).all()
    doctoravailability=Doctoravailability.query.filter_by(doctor_id=doctor_id).all()
    patients=[]
    for appointment in appointments:
        patient=User.query.get(appointment.patient_id)
        if patient and patient not in patients:
            patients.append(patient)
    return render_template('Doctor_Dashboard.html',this_user=this_user,appointments=appointments,patients=patients,doctoravailability=doctoravailability)

@app.route('/update_patient_history/<int:patient_id>/<int:doctor_id>/<int:appointment_id>',methods=['GET','POST'])
def update_patient_history(patient_id,doctor_id,appointment_id):
    doctor=User.query.get(doctor_id)
    patient=User.query.get(patient_id)
    appointment=Appointment.query.get(appointment_id)
    department=appointment.department

    if request.method=='POST':
        visit_type=request.form.get('visit_type')
        test_done=request.form.get('test_done')
        diagnosis=request.form.get('diagnosis')
        prescription=request.form.get('prescription')
        medicines=request.form.get('medicines')
        medications=request.form.get('medications')
        cost=request.form.get('cost')
        
        treatment=Treatment(diagnosis=diagnosis,cost=cost,medicines=medicines,prescription=prescription,visit_type=visit_type,test_done=test_done,appointment_id=appointment_id,patient_id=patient.id,doctor_id=doctor.id,medications=medications)
        db.session.add(treatment)
        db.session.commit()
        return redirect(url_for('patient_history_doctor',doctor_id=doctor.id,patient_id=patient.id))
    return render_template('UpdatePatientHistory.html',doctor=doctor,patient=patient,appointment=appointment,department=department)

@app.route('/patient_history_doctor/<int:doctor_id>/<int:patient_id>',methods=['GET','POST'])
def patient_history_doctor(doctor_id,patient_id):
    doctor=User.query.get(doctor_id)
    patient=User.query.get(patient_id)
    treatments=Treatment.query.filter_by(doctor_id=doctor.id).all()
    department=Department.query.get(doctor.department_id)
    return render_template("Patienthistory_Doctor.html",treatments=treatments,department=department,doctor=doctor,patient=patient)

@app.route('/provide_availability/<int:doctor_id>',methods=['GET','POST'])
def provide_availability(doctor_id):
    this_user=User.query.get(doctor_id)

    today=datetime.today()
    days=[]
    for x in range(7):
        day=today+timedelta(days=x)
        days.append(day.strftime('%d-%m-%Y'))
    
    if request.method=='POST':
        for date in days:
            selected_slots='availability_'+date
            slots=request.form.getlist(selected_slots)
            for slot in slots:
                availability=Doctoravailability(doctor_id=this_user.id,date=date,slot=slot)
                db.session.add(availability)
        db.session.commit()
        return redirect(url_for('doctor_dashboard',doctor_id=this_user.id))
    return render_template('Availability_Doctor.html',doctor=this_user,days=days)

@app.route('/book_appointment/<int:patient_id>/<int:availability_id>',methods=['GET','POST'])
def book_appointment(patient_id,availability_id):
    this_user=User.query.get(patient_id)
    availability=Doctoravailability.query.get(availability_id)
    doctor=User.query.get(availability.doctor_id)
    appointment=Appointment(patient_id=this_user.id,doctor_id=doctor.id,department_id=doctor.department_id,date=availability.date,time=availability.slot,status='pending')
    db.session.add(appointment)
    db.session.commit()
    return redirect(url_for('patients_dashboard',patient_id=this_user.id))

@app.route('/availability_doctor/<int:doctor_id>')
def availability_doctor(doctor_id):
    doctor=User.query.get(doctor_id)
    doctoravailability=Doctoravailability.query.filter_by(doctor_id=doctor_id).all()
    return render_template('Availability_Doctor.html',doctor=doctor,doctoravailability=doctoravailability)

@app.route('/completed_appointment/<int:appointment_id>/<int:doctor_id>',methods=['GET','POST'])
def completed_appointment(appointment_id,doctor_id):
    appointment=Appointment.query.get(appointment_id)
    if appointment:
        appointment.status='completed'
        db.session.commit()
    return redirect(url_for('doctor_dashboard',doctor_id=doctor_id))

@app.route('/cancel_appointment/<int:appointment_id>/<int:this_user_id>',methods=['GET','POST'])
def cancel_appointment(appointment_id,this_user_id):
    appointment=Appointment.query.get(appointment_id)
    this_user=User.query.get(this_user_id)
    if appointment:
        appointment.status='cancelled'
        db.session.commit()
    if this_user.role=='patient':
        return redirect(url_for('patients_dashboard',patient_id=this_user_id))
    elif this_user.role=='doctor':
        return redirect(url_for('DoctorDashboard',doctor_id=this_user_id))
    else:
        return redirect('/login')


##patients_dashboard

@app.route('/patients_dashboard/<int:patient_id>',methods=['GET','POST'])
def patients_dashboard(patient_id):
    this_user=User.query.get(patient_id)
    departments=Department.query.all()
    appointments=Appointment.query.filter_by(patient_id=this_user.id).all()
    treatments=Treatment.query.filter_by(patient_id=this_user.id).all()
    
    search=request.args.get('q','').strip()
    
    if search:
        departments=Department.query.filter(
            Department.name.ilike(f"%{search}%")).all()
    else:
        departments=Department.query.all()
    doctors=User.query.filter_by(role='doctor').all()
    return render_template('Patients_Dashboard.html',this_user=this_user,appointments=appointments,treatments=treatments,departments=departments,doctors=doctors,search=search)

@app.route('/editpatient_patient/<int:patient_id>',methods=['GET','POST'])
def editpatient_patient(patient_id):
    this_user=User.query.get(patient_id)

    if request.method=='POST':
        this_user.username=request.form.get('username')
        this_user.contact_number=request.form.get('contact_number')
        this_user.gender=request.form.get('gender')
        this_user.dob=request.form.get('dob')
        
        db.session.commit()
        return redirect(url_for('patients_dashboard',patient_id=this_user.id))
    return render_template('Edit_Patient_Patient.html',this_user=this_user)

@app.route('/patient_history_patient/<int:patient_id>')
def patient_history_patient(patient_id):
    this_user=User.query.get(patient_id)
    treatments=Treatment.query.filter_by(patient_id=this_user.id).all()
    for treatment in treatments:
        treatment.doctor=User.query.get(treatment.doctor_id)
    return render_template("Patienthistory_patient.html",this_user=this_user,treatments=treatments)

@app.route('/availability_patient/<int:doctor_id>/<int:patient_id>',methods=['GET','POST'])
def availability_patient(doctor_id,patient_id):
    doctor=User.query.get(doctor_id)
    this_user=User.query.get(patient_id)

    doctoravailability=Doctoravailability.query.filter_by(doctor_id=doctor_id).all()
    appointments=Appointment.query.filter_by(doctor_id=doctor_id).all()
    b_slots={(appointment.date,appointment.time)  for appointment in appointments if appointment.status!='cancelled' }
    for availability in doctoravailability:
        if (availability.date,availability.slot) in b_slots:
            availability.is_booked=True
        else:
            availability.is_booked=False
    return render_template('Availability_Patient.html',doctor=doctor,doctoravailability=doctoravailability,this_user=this_user)

@app.route('/view_department/<int:department_id>/<int:patient_id>')
def view_department(department_id,patient_id):
    department=Department.query.get(department_id)
    doctors=User.query.filter_by(department_id=department_id).all()
    this_user=User.query.get(patient_id)
    return render_template('View_Department.html',department=department,doctors=doctors,this_user=this_user)

@app.route('/view_doctor_details/<int:doctor_id>/<int:patient_id>')
def view_doctor_details(doctor_id,patient_id):
    doctor=User.query.get(doctor_id)
    this_user=User.query.get(patient_id)
    availability=Doctoravailability.query.filter_by(doctor_id=doctor_id).all()
    return render_template('View_Doctor_Details.html',doctor=doctor,this_user=this_user,availability=availability)