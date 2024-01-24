from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm, EntryForm
from flask_sqlalchemy import SQLAlchemy

from datetime import *

app=Flask(__name__,static_folder='static')
    
app.config['SECRET_KEY']='JhRvPw5sL8y2TkQz'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'


db=SQLAlchemy(app)


class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(20),unique=True,nullable=False)
    password=db.Column(db.String(20),nullable=False)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    category=db.Column(db.String(100),nullable=False)
    date_added=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    content=db.Column(db.String(100),nullable=False)
    amount=db.Column(db.String(100),nullable=False)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_added},'{self.category}''"




@app.route("/")
def home():
    return render_template('homepage.html')



@app.route("/about")
def about():
    return("<h1>This is the about page</h1>")



@app.route("/main")
def mainpage():
    entries=Post.query.all()
    return render_template('main.html',entries=entries)

@app.route("/analysis")
def analysis():
    return render_template('analysis.html')


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


@app.route("/entry/new",methods=['GET','POST'])
def new_post():
    form=EntryForm()
    if form.validate_on_submit():
        entry=Post(category=form.category.data,content=form.content.data,amount=form.amount.data)
        db.session.add(entry)
        db.session.commit()
        flash('Entry successful!','success')
        return redirect(url_for('mainpage')) 
    return render_template('entry.html',title="new entry",form=form)

