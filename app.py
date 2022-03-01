from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

local_server=True
with open('config.json','r') as c:
    params=json.load(c)["params"]
app = Flask(__name__)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_url']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_url']

db = SQLAlchemy(app)

class Contact(db.Model):
    '''sr_no, name, phone,message, date,email    '''
    sr_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    date = db.Column(db.String(25), nullable=True)
    message = db.Column(db.String(120), nullable=False) 
    email = db.Column(db.String(25), nullable=False)

@app.route("/")
def home():
    return render_template('index.html',params=params)

@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/post")
def post():
    return render_template('post.html',params=params)

@app.route("/contact" , methods = ['GET','POST'])
def contact():
    if request.method=='POST':
        '''Add data to the form'''
        name_v=request.form.get('name')
        email_v=request.form.get('email')
        phone_v=request.form.get('phone')
        message_v=request.form.get('message')

        '''sr_no, name, phone,message, date,email    '''
        entry= Contact(name=name_v,phone=phone_v,message=message_v,date=datetime.now(),email=email_v)
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html',params=params)


app.run(debug=True)