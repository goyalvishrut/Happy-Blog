from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json

local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)

app.config.update(MAIL_SERVER='smtp.gmail.com',
                  MAIL_PORT='465',
                  MAIL_USE_SSL=True,
                  MAIL_USERNAME = params['gmail_user'],
                  MAIL_PASSWORD = params['gmail_password'])

mail = Mail(app)
if (local_server):
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

class Posts(db.Model):
    '''sr_no, title, slug,content, date,writer    '''
    sr_no = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(10000), nullable=True)
    date = db.Column(db.String(25), nullable=True)
    writer = db.Column(db.String(25), nullable=False)
    img_file = db.Column(db.String(50), nullable=True)


@app.route("/")
def home():
    posts=Posts.query.filter_by().all()[0:params['numbers_of_posts']]
    return render_template('index.html', params=params, posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        '''Add data to the form'''
        name_v = request.form.get('name')
        email_v = request.form.get('email')
        phone_v = request.form.get('phone')
        message_v = request.form.get('message')
        '''sr_no, name, phone,message, date,email    '''
        entry = Contact(name=name_v,
                        phone=phone_v,
                        message=message_v,
                        date=datetime.now(),
                        email=email_v)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name_v + ' (HAPPY BLOG)',
                          sender=email_v,
                          recipients=[params['gmail_user']],
                          body=message_v + "\n" + phone_v)
    return render_template('contact.html', params=params)


app.run(debug=True)