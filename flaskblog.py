from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import *

app=Flask(__name__,static_folder='static')
    


app.config['SECRET_KEY']='JhRvPw5sL8y2TkQz'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'


db=SQLAlchemy()
db.init_app(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(20),unique=True,nullable=False)
    password=db.Column(db.String(20),nullable=False)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    content=db.Column(db.String(100),nullable=False)
    date_added=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    amount=db.Column(db.Text,nullable=False)
    category=db.Column(db.String(100),nullable=False)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_added},'{self.category}''"













entries=[{"Name":"Pizza","Date":"17/1/24","Amount":500,"Title":"Food"},
            {"Name":"Donuts","Date":"20/1/24","Amount":200,"Title":"Food"},
            {"Name":"Mac-Book","Date":"23/1/24","Amount":98000,"Title":"Electronics"}
            

]

















@app.route("/")
def home():
    return render_template('homepage.html')


#@app.route("/LoginPage.html")
#def login():
    #return render_template('LoginPage.html')

@app.route("/about")
def about():
    return("<h1>This is the about page</h1>")



@app.route("/main")
def mainpage():
    return render_template('main.html',entries=entries)


@app.route("/register", methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        flash("Account Created!",'success')
        return redirect(url_for('mainpage'))
    
    return render_template('samplesignup.html',form=form)

@app.route("/login",methods=['GET','POST'])
def login1():
    form=LoginForm()
    if form.validate_on_submit():
        if form.email.data=='riyashet10@gmail.com' and form.password.data=='3xp3n53':
            flash("You have been logged in!",'success')
            return redirect(url_for('mainpage'))
        else:
            flash("Incorrect Credentials",'danger')

    return render_template('samplelogin.html',form=form)
