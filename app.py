from flask import Flask, render_template ,request ,session ,flash ,url_for, redirect 
from flask_sqlalchemy import SQLAlchemy
import os

crdr=os.path.dirname(os.path.abspath(__file__))
#give absolute path of current file

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quizapp.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = '23f2002351'

db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

#if table name is not specified, it will be same as class name in lower case
class User(db.Model):
    __tablename__ = "User_table"
    #Userid for the table
    id = db.Column(db.Integer, primary_key=True)
    User_email = db.Column(db.String(120), unique=True, nullable=False)
    User_fullname = db.Column(db.String(120), nullable=False)
    User_password = db.Column(db.String(120), nullable=False)
    User_qualification = db.Column(db.String(120), nullable=False)
    User_dob = db.Column(db.String(120), nullable=False)
    isadmin = db.Column(db.Boolean, nullable=False,default=False)
    Marks = db.relationship('Marks',back_populates='User',cascade='all,delete-orphan')

class Subject(db.Model):
    __tablename__ = "Subject_table"
    sub_id = db.Column(db.Integer, primary_key=True)
    sub_name = db.Column(db.String(80), nullable=False)
    sub_code = db.Column(db.String(120), nullable=False)
    sub_description = db.Column(db.String(120), nullable=False)
    sub_teacher = db.Column(db.String(120), nullable=False)
    chap=db.relationship('Chapter',back_populates='Subject',cascade="all, delete-orphan")
    
class Chapter(db.Model):
    __tablename__ = "chapter_table"
    ch_name = db.Column(db.String(80), nullable=False)
    ch_id = db.Column(db.Integer, primary_key=True)
    ch_desc = db.Column(db.String(120), nullable=False)
    sub_id = db.Column(db.Integer,db.ForeignKey("Subject_table.sub_id"), nullable=False)
    Subject=db.relationship('Subject',back_populates='chap')
    quiz=db.relationship('Quizzes',back_populates='chap',cascade="all, delete-orphan")

class Quizzes(db.Model):
    __tablename__ = "quiz_table"
    qz_id= db.Column(db.Integer, primary_key=True)   
    qz_ch_id = db.Column(db.Integer, db.ForeignKey("chapter_table.ch_id"), nullable=False)
    qz_name= db.Column(db.String(80), nullable=False)
    qz_code= db.Column(db.String(120), nullable=False)
    qz_desc_remarks= db.Column(db.String(120), nullable=False)
    qz_questions= db.Column(db.String(120), nullable=False)
    qz_date= db.Column(db.String(120), nullable=False)
    qz_time_duration= db.Column(db.String(15), nullable=False)

    chap=db.relationship('Chapter',back_populates='quiz')
    question=db.relationship('questions',back_populates='quiz',cascade="all, delete-orphan")
    Marks=db.relationship('Marks',back_populates ='quiz',cascade="all, delete-orphan")

class questions(db.Model):
    __tablename__ = "question_table"
    q_id = db.Column(db.Integer, primary_key=True)
    q_statement=db.Column(db.String(120), nullable=False)
    ans_opt1=db.Column(db.String(120), nullable=False)
    ans_opt2=db.Column(db.String(120), nullable=False)
    ans_opt3=db.Column(db.String(120), nullable=False)
    ans_opt4=db.Column(db.String(120), nullable=False)
    ans_correct=db.Column(db.String(120), nullable=False)
    qz_id=db.Column(db.Integer,db.ForeignKey("quiz_table.qz_id"), nullable=False)
    quiz=db.relationship('Quizzes',back_populates='question')

class Marks(db.Model):
    __tablename__ = "marks_table"
    mark_id = db.Column(db.Integer, primary_key=True)
    mark_User_id = db.Column(db.Integer, db.ForeignKey("User_table.id"), nullable=False)
    mark_quiz_id = db.Column(db.Integer, db.ForeignKey("quiz_table.qz_id"), nullable=False)
    mark_score = db.Column(db.Integer, nullable=False)
    time_taken=db.Column(db.DateTime, nullable=False)
    quiz=db.relationship('Quizzes',back_populates='Marks')
    User=db.relationship('User',back_populates='Marks')

def admincreation():
    admin=User.query.filter(User.User_email== "admin@gmail.com").first()
    if admin is None:
        admin = User(
            User_email="admin@gmail.com",
            User_fullname="admin",
            User_password="admin@123",
            User_qualification="B.Sc Data Science IITM",
            User_dob="01-01-1999",
            isadmin=True)
        db.session.add(admin)
        db.session.commit()
        db.create_all()
admincreation() 

@app.route("/")
def hello_world():
    return redirect('/login')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        email = request.form.get("emailaddress")
        password = request.form.get("password")
        user = User.query.filter_by(User_email = email).first()
          
        print(User.User_password)
        if user :
            session['isadmin'] = False
            if user.isadmin:
                session['isadmin'] = True
                if user.User_password == password:
                    session['password'] = user.User_password
                    session['id']= user.id
                    return redirect('/admin')
                else:
                    flash('incorrect  password','error')
                    return redirect('/login')
            else:
                if (user.User_password == password):
                    session['password'] = user.User_password
                    session['id']= user.id
                    return redirect('/user')
                else:
                    flash('incorrector password','error')
                    return redirect('/login')
        else:
            flash('user not found','error')
            return redirect('/login')
        
#create signup route
# create a route for signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    if request.method == 'POST':    
        email = request.form.get("emailaddress")
        fullname = request.form.get("fullname") 
        password = request.form.get("password")
        qualification = request.form.get("qualification")    
        dob = request.form.get("dob")
        user = User.query.filter_by(User_email =  email).first()    
        if user:
            flash('user already exists','error')
            return redirect('/signup')
        else:    
            user = User(User_email=email,User_fullname=fullname,User_password=password,User_qualification=qualification,User_dob=dob)
            db.session.add(user)
            db.session.commit()
            flash('user created successfully','info')
            return redirect('/login')    

@app.route('/admin')
def adminpage():
    if session.get('isadmin'):
                #tablename.query.all()  
        subjects = Subject.query.all()
        return render_template('admin.html',Subjects=subjects)
    else:
        return redirect('/login')
    
@app.route('/admin/logout')
def adminlogout():
    session.clear()
    flash('admin logged out successfully','info')
    return redirect('/login')

@app.route('/subjectcreation', methods=['GET', 'POST'])
def subjectcreation():
    if session.get('isadmin'):
        if request.method == 'POST':
            sub_name = request.form.get("sub_name")
            sub_code = request.form.get("sub_code")
            sub_description = request.form.get("sub_description")
            sub_teacher = request.form.get("sub_teacher")
            sub = Subject(sub_name=sub_name,sub_code=sub_code,sub_description=sub_description,sub_teacher=sub_teacher)
            db.session.add(sub)
            db.session.commit()
            return redirect('/admin')
        else:
            return render_template('subjectcreation.html')
    return redirect('/login')
    

@app.route('/editSubject/<int:sub_id>', methods=['GET', 'POST'])
def editSubject(sub_id):
    if session.get('isadmin'):
        sub=Subject.query.filter_by(sub_id=sub_id).first()
        if not sub:
            return redirect('/admin')        
        if request.method == 'POST':
            sub_name = request.form.get("sub_name")
            sub_code = request.form.get("sub_code")
            sub_description = request.form.get("sub_description")
            sub_teacher = request.form.get("sub_teacher")
        #    sub = Subject(sub_name=sub_name,sub_code=sub_code,sub_description=sub_description,sub_teacher=sub_teacher)
        #    db.session.add(sub)
            sub.sub_name=sub_name
            sub.sub_code=sub_code
            sub.sub_description=sub_description
            sub.sub_teacher=sub_teacher
            db.session.commit()
            return redirect('/admin')
        else:
            return render_template('editSubject.html',subject=sub)
    else:
        flash('only admin can edit','error')
    return redirect('/login')

@app.route('/deleteSubject/<int:sub_id>', methods=['GET', 'POST'])
def deleteSubject(sub_id):
    if session.get('isadmin'):
        sub=Subject.query.filter_by(sub_id=sub_id).first()
        if not sub:
            flash('subject not found','error')
            return redirect('/admin')
        if request.method == 'POST':
            db.session.delete(sub)
            db.session.commit()
            return redirect('/admin')
        else:
            flash('no deletion is done, use proper method','error')
        return redirect('/admin')
    else:
        flash('only admin can delete','error')
    return redirect('/login')



if __name__ == "__main__":
    app.run(debug=True)
