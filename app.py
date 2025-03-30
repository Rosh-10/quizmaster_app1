from flask import Flask, render_template ,request ,session ,flash ,url_for, redirect 
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

#for summarizing charts 
import seaborn as sns
import matplotlib as math
math.use('Agg')
import matplotlib.pyplot as plt
#give absolute path of current file
crdr=os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quizapp.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = '23f2002351'
app.config['UPLLOAD_FOLDER']=os.path.join(crdr,"static","imgs")

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
    qz_date= db.Column(db.Date, nullable=False)
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
    ans_correct=db.Column(db.Integer, nullable=False)
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

db.create_all()
#
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
        if user :
            session['isadmin'] = False
            session['useremail']=user.User_email
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
                    return redirect('/userdashboard')
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
        user=User.query.filter_by(isadmin=False).all()
        subject=Subject.query.all()
        chapter=Chapter.query.all()
        quiz=Quizzes.query.all()
        marks=Marks.query.all()
                #tablename.query.all()  
        return render_template('admin.html',user=user,subject=subject,chapter=chapter,quizzes=quiz,marks=marks)
    else:
        return redirect('/login')

@app.route('/adminUser/<int:user_id>', methods=['GET', 'POST'])
def adminuserpage(user_id):
    if session.get('isadmin'):
        user=User.query.filter_by(id=user_id).first()
        marks=Marks.query.filter_by(mark_User_id=user_id).all()
        print("User:",user)
        print("Marks:",marks)
        return render_template('adminUser.html',user=user)
    return redirect('/login')

@app.route('/adminSubject', methods=['GET', 'POST'])
def admin_allsubjectpage():
    if session.get('isadmin'):
                #tablename.query.all()  
        subjects = Subject.query.all()
        return render_template('adminSubject.html',Subjects=subjects)
    
    return redirect('/login')

@app.route('/adminChapter', methods=['GET', 'POST'])
def admin_allchapterpage():
    if session.get('isadmin'):
        chapters = Chapter.query.all()
        subjects = Subject.query.all()
        return render_template('adminChapter.html', Chapters=chapters, Subjects=subjects)
    return redirect('/login')


@app.route('/adminSubject/<int:sub_id>', methods=['GET', 'POST'])
def subjectpage(sub_id):
    if session.get('isadmin'):
        subject = Subject.query.filter_by(sub_id=sub_id).first()
        chapter = Chapter.query.filter_by(sub_id=sub_id).all()
        return render_template('subject_view.html',subject=subject,chapters=chapter)
    return redirect('/login')

@app.route('/adminChapter/<int:ch_id>', methods=['GET', 'POST'])
def chapterpage(ch_id):
    if session.get('isadmin'):
        
        chapter = Chapter.query.filter_by(ch_id=ch_id).first()
        
        quizzes = Quizzes.query.filter_by(qz_ch_id=ch_id).all()
        
        return render_template('chapter_view.html',chapter=chapter,quizzes=quizzes)
    return redirect('/login')
    
@app.route('/adminQuiz/<int:qz_id>', methods=['GET', 'POST'])
def quizpage(qz_id):
    if session.get('isadmin'):
        quiz = Quizzes.query.filter_by(qz_id=qz_id).first()
        qts = questions.query.filter_by(qz_id=qz_id).all()
        return render_template('quiz_view.html',quiz=quiz,qts=qts)
    return redirect('/login')


    
@app.route('/admin/logout')
def adminlogout():
    session.clear()
    flash('admin logged out successfully','info')
    return redirect('/login')

@app.route('/admin_userlist',methods=['GET', 'POST'])
def userlist():
    if session.get('isadmin'):
        users = User.query.filter_by(isadmin=False).all()
        return render_template('admin_userlist.html',Users=users)
    return redirect('/admin')

#creation of subject, user, chapters and quizzes
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
            return redirect('/adminSubject')
        else:
            return render_template('subjectcreation.html')
    return redirect('/login')

@app.route('/usercreation', methods=['GET', 'POST'])
def usercreation():
    if session.get('isadmin'):
        if request.method == 'POST':
            User_email = request.form.get("User_email")
            User_fullname = request.form.get("User_fullname")
            User_password = request.form.get("User_password")
            User_qualification = request.form.get("User_qualification")
            User_dob = request.form.get("User_dob")
            existing_user = User.query.filter_by(User_email=User_email).first()
            if existing_user:
                
                flash("Email already exists!", "error")
                return redirect(request.url)

            user = User(User_email=User_email,User_fullname=User_fullname,User_password=User_password,User_qualification=User_qualification,User_dob=User_dob,isadmin=False)
            db.session.add(user)
            db.session.commit()
            users = User.query.filter_by(isadmin=False).all()
            
            return render_template('admin_userlist.html', Users=users)
        return redirect('/admin')
    return redirect('/login')


@app.route('/chaptercreation/<int:sub_id>', methods=['GET', 'POST'])
def chaptercreation(sub_id):
    if session.get('isadmin'):
        if request.method == 'POST':
            ch_name = request.form.get("ch_name")
            ch_desc = request.form.get("ch_desc")
            chap = Chapter(ch_name=ch_name,ch_desc=ch_desc,sub_id=sub_id)
            db.session.add(chap)
            db.session.commit()
            return redirect(url_for('subjectpage',sub_id=sub_id))
        else:
            return render_template('chaptercreation.html',sub_id=sub_id)
    return redirect('/login')


@app.route('/quizcreation/<int:ch_id>', methods=['GET', 'POST'])
def quizcreation(ch_id):
    
    if session.get('isadmin'):
        if request.method == 'POST':
            qz_name = request.form.get("qz_name")
            qz_code = request.form.get("qz_code")
            qz_desc_remarks = request.form.get("qz_desc_remarks")
            qz_date = request.form.get("qz_date")
            qz_time_duration = request.form.get("qz_time_duration")
            qzd=datetime.strptime(qz_date, '%Y-%m-%d')

           
            quiz = Quizzes(qz_name=qz_name,qz_code=qz_code,qz_desc_remarks=qz_desc_remarks,qz_date=qzd,qz_time_duration=qz_time_duration,qz_ch_id=ch_id)
            
            
            db.session.add(quiz)
            db.session.commit()
            return redirect(url_for('chapterpage',ch_id=ch_id))
        else:
            return render_template('quizcreation.html',ch_id=ch_id)
    return redirect('/login')

@app.route('/questioncreation/<int:qz_id>', methods=['GET', 'POST'])
def questioncreation(qz_id):
    if session.get('isadmin'):
        if request.method == 'POST':
            qstn = request.form.get("question")
            opt1 = request.form.get("option1")
            opt2 = request.form.get("option2")
            opt3 = request.form.get("option3")
            opt4 = request.form.get("option4")
            ans = request.form.get("correct_option")
            qts = questions(q_statement=qstn,ans_opt1=opt1,ans_opt2=opt2,ans_opt3=opt3,ans_opt4=opt4,ans_correct=ans,qz_id=qz_id)
            print(qts)
            print(qts.q_statement,qts.ans_opt1,qts.ans_opt2,qts.ans_opt3,qts.ans_opt4,qts.ans_correct)
            db.session.add(qts)
            db.session.commit()
            return redirect(url_for('quizpage',qz_id=qz_id))
        else:
            return render_template('questioncreation.html',qz_id=qz_id)
    return redirect('/login')
#updating user,subject and chapter,quizzes

@app.route('/editUser/<int:user_id>', methods=['GET', 'POST'])
def editUser(user_id):
    if session.get('isadmin'):
        user=User.query.filter_by(id=user_id).first()
        
        if user == None:
            flash('no user found', 'error')
            return redirect('/admin')       
        if request.method == 'POST':
            User_email = request.form.get("User_email")
            User_fullname = request.form.get("User_fullname")
            User_password = request.form.get("User_password")
            User_qualification = request.form.get("User_qualification")
            User_dob = request.form.get("User_dob")
        
        #    sub = Subject(sub_name=sub_name,sub_code=sub_code,sub_description=sub_description,sub_teacher=sub_teacher)
        #    db.session.add(sub)
            user.User_email=User_email
            user.User_fullname=User_fullname
            user.User_password=User_password
            user.User_qualification=User_qualification
            user.User_dob=User_dob
            db.session.commit()
            users=User.query.filter(User.isadmin ==False).all()
            return render_template('admin_userlist.html',Users=users)
    flash('kicked out','error')
    return redirect('/admin')



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
            return redirect('/adminSubject')
        else:
            return render_template('editSubject.html',subject=sub)
    else:
        flash('only admin can edit','error')
    return redirect('/login')

@app.route('/editChapter/<int:ch_id>', methods=['GET', 'POST'])
def editChapter(ch_id):
    if session.get('isadmin'):
        chapters=Chapter.query.filter_by(ch_id = ch_id).first()
        if not chapters:
            flash('no chapters with that chapter_id','error')
            return redirect('/admin')        
        if request.method == 'POST':
            ch_name = request.form.get("ch_name")
            ch_desc = request.form.get("ch_desc")
        #    sub = Subject(sub_name=sub_name,sub_code=sub_code,sub_description=sub_description,sub_teacher=sub_teacher)
        #    db.session.add(sub)
            chapters.ch_name=ch_name
            chapters.ch_desc=ch_desc
            db.session.commit()
            flash('chapter edited successfully','info')
            sub_id=chapters.sub_id
            sub=Subject.query.filter_by(sub_id=sub_id).first()
            
            return redirect(url_for('subjectpage',sub_id=sub_id))
        else:
            return render_template('editChapter.html',chapter = chapters)
    else:
        flash('only admin can edit','error')
    return redirect('/login')

@app.route('/editQuiz/<int:qz_id>', methods=['GET', 'POST'])
def editQuiz(qz_id):
    if session.get('isadmin'):
        quiz=Quizzes.query.filter_by(qz_id = qz_id).first()
        if not quiz:
            flash('no quiz with that quiz_id','error')
            return redirect('/admin')        
        if request.method == 'POST':
            qz_name = request.form.get("qz_name")
            qz_code = request.form.get("qz_code")
            qz_desc_remarks = request.form.get("qz_desc_remarks")
            qz_date = request.form.get("qz_date")
            qz_time_duration = request.form.get("qz_time_duration")
            qzd=datetime.strptime(qz_date, '%Y-%m-%d')
            
            quiz.qz_name=qz_name
            quiz.qz_code=qz_code
            quiz.qz_desc_remarks=qz_desc_remarks
            quiz.qz_date=qzd
            quiz.qz_time_duration=qz_time_duration
            
            db.session.commit()
            flash('chapter edited successfully','info')
            ch_id=quiz.qz_ch_id
            return redirect(url_for('chapterpage',quiz=quiz,ch_id=qz_id))
            
        else:
            return render_template('editQuiz.html',quiz=quiz ,qz_id=qz_id)
    else:
        flash('only admin can edit','error')
    return redirect('/login')

#editQuestion
@app.route('/editQuestion/<int:q_id>', methods=['GET', 'POST'])
def editQuestion(q_id):
    if session.get('isadmin'):
        question=questions.query.filter_by(q_id = q_id).first()
        if not question:
            flash('no question with that question_id','error')
            return redirect('/admin')        
        if request.method == 'POST':
            qstn = request.form.get("question")
            opt1 = request.form.get("option1")
            opt2 = request.form.get("option2")
            opt3 = request.form.get("option3")
            opt4 = request.form.get("option4")
            ans = request.form.get("correct_option")
            
            question.q_statement=qstn
            question.ans_opt1=opt1
            question.ans_opt2=opt2
            question.ans_opt3=opt3
            question.ans_opt4=opt4
            question.ans_correct=ans

            db.session.commit()
            flash('question edited successfully','info')
            qz_id=question.qz_id
            return redirect(url_for('quizpage',qz_id=qz_id))
        else:
            return render_template('editQuestion.html',question=question ,q_id=q_id)
    else:
        flash('only admin can edit','error')
    return redirect('/login')


#deleting user,subject,chapter and quizzes

@app.route('/deleteSubject/<int:sub_id>', methods=['GET', 'POST'])
def deleteSubject(sub_id):
    if session.get('isadmin'):
        sub=Subject.query.filter_by(sub_id=sub_id).first()  
        print(sub)
        if not sub:
            flash('subject not found','error')
            return redirect('/admin')
        if request.method == 'POST' :
            db.session.delete(sub)
            db.session.commit()
            flash('subject deleted successfully','info')
            return redirect('/adminSubject') 
        else:
            flash('no deletion is done, use proper method','error')
        return redirect('/admin')
    else:
        flash('only admin can delete','error')
    return redirect('/login')

@app.route('/deleteUser/<int:user_id>', methods=['GET', 'POST'])
def deleteUser(user_id):
    if session.get('isadmin'):
        user=User.query.filter_by(id=user_id).first()
        if not user:
            flash('subject not found','error')
            return redirect('/admin_userlist')
        if request.method == 'POST':
            db.session.delete(user)
            db.session.commit()
            flash('user deleted successfully','info')
            return redirect('/admin_userlist')
        else:
            flash('no deletion is done, use proper method','error')
        return redirect('/admin')
    else:
        flash('only admin can delete','error')
    return redirect('/login')

@app.route('/deleteChapter/<int:ch_id>', methods=['GET', 'POST'])
def deleteChapter(ch_id):
    if session.get('isadmin'):
        chapter=Chapter.query.filter_by(ch_id=ch_id).first()
        if not chapter:
            flash('chapter not found','error')
            return redirect('/adminSubject')
        if request.method == 'POST':
            db.session.delete(chapter)
            db.session.commit()
            flash('chapter deleted successfully','info')
            sub_id=chapter.sub_id
            return redirect(url_for('subjectpage',sub_id=sub_id))
        else:
            flash('no deletion is done, use proper method','error')
    else:
        flash('only admin can delete','error')
    return redirect('/login')

@app.route('/deleteQuiz/<int:qz_id>', methods=['GET', 'POST'])
def deleteQuiz(qz_id):
    if session.get('isadmin'):
        quiz = Quizzes.query.filter_by(qz_id=qz_id).first()
        if not quiz:
            flash('quiz not found', 'error')
            return redirect('/admin')
        if request.method == 'POST':
            db.session.delete(quiz)
            db.session.commit()
            flash('quiz deleted successfully', 'info')
            ch_id = quiz.qz_ch_id
            return redirect(url_for('chapterpage', ch_id=ch_id))
        else:
            flash('no deletion is done, use proper method', 'error')
    else:
        flash('only admin can delete', 'error')
    return redirect('/login')

@app.route('/deleteQuestion/<int:q_id>', methods=['GET', 'POST'])
def deleteQuestion(q_id):
    if session.get('isadmin'):
        question = questions.query.filter_by(q_id=q_id).first()
        if not question:
            flash('question not found', 'error')
            return redirect('/admin')
        if request.method == 'POST':
            db.session.delete(question)
            db.session.commit()
            flash('question deleted successfully', 'info')
            qz_id = question.qz_id
            return redirect(url_for('quizpage', qz_id=qz_id))
        else:
            flash('no deletion is done, use proper method', 'error')
    else:
        flash('only admin can delete', 'error')
    return redirect('/login')

#creating user dashboard to show quizzes available

@app.route('/user/logout')
def userlogout():
    session.clear()
    flash('user logged out successfully','info')
    return redirect('/login')
@app.route('/userdashboard')
def userdashboard():
    if session.get('password'):
        user_id=session['id']
        quizzes = Quizzes.query.all()
        user=User.query.filter_by(id=user_id).first()
        marks = Marks.query.filter_by(mark_User_id=user_id).all()
        return render_template('userdashboard.html',quizzes=quizzes,user=user,marks=marks)
    return redirect('/login')


@app.route('/user/quiz/<int:qz_id>', methods=['GET', 'POST'])
#creating start page for quiz for user
def quizstart(qz_id):
    if session.get('password'):
        session['quizstarttime']=datetime.now()
        quiz = Quizzes.query.filter_by(qz_id=qz_id).first()
        questions_list = questions.query.filter_by(qz_id=qz_id).all()
        #based on datetime, show quiz availablity and flash messagesand redirect accordingly
        #check if quiz date is in the past
        flash('Quiz is available','info')
       
        if len(questions_list) == 0:
            flash('No questions found in this quiz','error')
            return redirect('/userdashboard')
       
      
        return redirect('/quiz/'+str(qz_id))
    return redirect('/login') 

@app.route('/quiz/<int:qz_id>', methods=['GET', 'POST'])
def quiz(qz_id):
    session['quizstarttime']=datetime.now()
    if session['useremail']:
        user_id = session['id']
        quiz = Quizzes.query.filter_by(qz_id=qz_id).first()
        questions_list = questions.query.filter_by(qz_id=qz_id).all()
        user = User.query.filter_by(id=user_id).first()
        return render_template('quiz.html', quiz=quiz, questions_list=questions_list,user=user)
    return  redirect('/login')

#create submit route for specific quiz id 
@app.route('/submitQuizAnswers/<int:qz_id>', methods=['POST'])

def submit_quiz(qz_id):
    print(session)
    if session['useremail']:
        user_id = session['id']
        user = User.query.filter_by(id=user_id).first()
        quiz = Quizzes.query.filter_by(qz_id=qz_id).first()
        questions_list = questions.query.filter_by(qz_id=qz_id).all()
        score = 0

        score=0
        for question in questions_list:
            answer = request.form.get(str(question.q_id))
            
            print('answer:',answer,question.ans_correct)
            if str(answer) == str(question.ans_correct):
                score += 1
            print('score:',score)
        time_taken=datetime.now()
        marks = Marks(mark_User_id=user_id, mark_quiz_id=qz_id, mark_score=score,time_taken=time_taken)
        db.session.add(marks)
        db.session.commit()
        return render_template('quiz_result.html', quiz=quiz,totalquestions=len(questions_list), questions_list=questions_list, score=score,user=user)
    else:
        return redirect('/userdashboard')

#creating new route for showing user history of previous quizzes
@app.route('/userhistory')
def userhistory():
    if session['useremail']:
        user_id = session['id']
        user = User.query.filter_by(id=user_id).first()
        marks = Marks.query.filter_by(mark_User_id=user_id).all()
        return render_template('userhistory.html', marks=marks,user=user)
    return redirect('/userdashboard')
#userprofile page with edit options for that user alone , should n't be able to edit other user

@app.route('/userprofile/<int:user_id>', methods=['GET', 'POST'])
def userprofile(user_id):
    print(dict(session))
    if session.get('useremail'):
        user = User.query.filter_by(id=user_id).first()
        if request.method == 'POST':
            User_email = request.form.get("User_email")
            User_fullname = request.form.get("User_fullname")
            User_password = request.form.get("User_password")
            User_qualification = request.form.get("User_qualification")
            User_dob = request.form.get("User_dob")
            user.User_email = User_email
            user.User_fullname = User_fullname
            user.User_password = User_password
            user.User_qualification = User_qualification
            user.User_dob = User_dob
            db.session.commit()
            flash('user edited successfully','info')
            return redirect('/userdashboard')
        else:
            return render_template('userprofile.html', user=user)
    return redirect('/login')
@app.route('/userprofile')
#creating route for search of users,subjects,chapters and quizzes with name
@app.route('/adminsearch', methods=['GET', 'POST'])
def search():
    if session.get('isadmin'):
        if request.method == 'GET':
            search_term = request.args.get('search_query')
            users = User.query.filter(User.User_fullname.ilike('%' + search_term + '%')).all()
            subjects = Subject.query.filter(Subject.sub_name.ilike('%' + search_term + '%')).all()
            chapters = Chapter.query.filter(Chapter.ch_name.ilike('%' + search_term + '%')).all()
            quizzes = Quizzes.query.filter(Quizzes.qz_name.ilike('%' + search_term + '%')).all()
            return render_template('adminsearchresult.html', users=users, subjects=subjects, chapters=chapters, quizzes=quizzes)
    return redirect('/login')

'''creating route for admin to view user, subject, chapter, quiz, and question dsummary charts
    it shows number of quizzes in each chapter,
     number of question in each quiz,
     number of chapters in each subject,
     number of quizzes in each chapter, 
'''

@app.route('/adminchart', methods=['GET', 'POST'])
def adminchart():
    if session.get('isadmin'):
        users = User.query.all()
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        quizzes = Quizzes.query.all()

        quiz_count_dict = {}
        for subject in subjects:
            quiz_count_dict[subject.sub_name] = 0
            chapters = Chapter.query.filter_by(sub_id=subject.sub_id).all()
            for chapter in chapters:
                quiz_count_dict[subject.sub_name] += len(Quizzes.query.filter_by(qz_ch_id=chapter.ch_id).all())

        subject_names = [key for key in quiz_count_dict]
        quiz_count = [value for value in quiz_count_dict.values() ]
        print(subject_names, quiz_count)
        plt.figure(figsize=(20,10))
        sns.barplot(x=subject_names,y=quiz_count)

        plt.title('Subject wise user attempts') 
        plt.xlabel('Subject name')
        plt.ylabel('Number of attempts')
        img1=os.path.join(crdr,"static","imgs","subject_quiz.png")
        if os.path.exists(img1):
                os.remove(img1)
        plt.savefig(img1,format='png')
        plt.close()

        marks = Marks.query.all()
        mark_user_dict = {}
        for user in users:
            if not user.isadmin:
                mark_user_dict[user.User_email] = (user.User_fullname, datetime.min, 0)
        for mark in marks:
            user = User.query.filter_by(id=mark.mark_User_id,isadmin=False).first()
            if user.User_email in mark_user_dict:
                if mark_user_dict[user.User_email][1] < mark.time_taken:
                    mark_user_dict[user.User_email] = (user.User_fullname, mark.time_taken, mark.mark_score)
        users_list = [value[0] for value in mark_user_dict.values()]
        marks_list = [value[2] if value[2] != 0 else 0 for value in mark_user_dict.values()]
        plt.figure(figsize=(6,10))
        sns.barplot(x=users_list, y=marks_list)
        plt.title('Users and marks') 
        plt.xlabel('User name')
        plt.ylabel('Marks')
        img_user_marks = os.path.join(crdr, "static", "imgs", "user_marks.png")
        if os.path.exists(img_user_marks):
            os.remove(img_user_marks)
        plt.savefig(img_user_marks, format='png')
        plt.close()

        quizzes = Quizzes.query.all()
        quiz_question_dict = {}
        for quiz in quizzes:
            quiz_question_dict[quiz.qz_name] = len(questions.query.filter_by(qz_id=quiz.qz_id).all())
        quiz_names = [key for key in quiz_question_dict]
        question_count = [value for value in quiz_question_dict.values()]
        plt.figure(figsize=(6,10))
        sns.barplot(x=quiz_names, y=question_count)
        plt.title('Quiz wise question') 
        plt.xlabel('Quiz name')
        plt.ylabel('Number of questions')
        img_quiz_questions = os.path.join(crdr, "static", "imgs", "quiz_question.png")
        if os.path.exists(img_quiz_questions):
            os.remove(img_quiz_questions)
        plt.savefig(img_quiz_questions, format='png')
        plt.close()

        marks = Marks.query.all()
        mark_user_dict = {}
        for user in users:
            if not user.isadmin:
                mark_user_dict[user.User_email] = 0
        for mark in marks:
            user = User.query.filter_by(id=mark.mark_User_id, isadmin=False).first()
            mark_user_dict[user.User_email] += 1
        users_list = [value for value in mark_user_dict.values()]
        plt.figure(figsize=(6,10))
        plt.pie(users_list, labels=[key for key in mark_user_dict], autopct='%1.1f%%')
        plt.title('Distribution of user attempts') 
        img_user_attempts = os.path.join(crdr, "static", "imgs", "user_attempts.png")
        if os.path.exists(img_user_attempts):
            os.remove(img_user_attempts)
        plt.savefig(img_user_attempts, format='png')
        plt.close()
   
        return render_template('adminchart.html', users=users, subjects=subjects, chapters=chapters, quizzes=quizzes)
    return redirect('/login')
    
    
if __name__ == "__main__":
    app.run(debug=True)
