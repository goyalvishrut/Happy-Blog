from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from flask_mail import Mail
import json

from pyparsing import PositionToken

local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'the random string'

app.config.update(MAIL_SERVER='smtp.gmail.com',
                  MAIL_PORT='465',
                  MAIL_USE_SSL=True,
                  MAIL_USERNAME=params['gmail_user'],
                  MAIL_PASSWORD=params['gmail_password'])

mail = Mail(app)
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_url']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_url']

app.config['UPLOADER_PATH'] = params['upload_location']

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
    '''sr_no, title,subtitle, slug,content, date,writer,img_file    '''
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
    posts = Posts.query.filter_by().all()[0:params['numbers_of_posts']]
    return render_template('index.html', params=params, posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_username']):
        if request.method == 'POST':
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOADER_PATH'],secure_filename(f.filename)))
            return ("Uploaded Successfuly")

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/edit/<string:post_sr_no>", methods=['GET','POST'])
def edit_route(post_sr_no):
    if ('user' in session and session['user'] == params['admin_username']):
        if (request.method == 'POST'):
            title_v = request.form.get('title')
            subtitle_v = request.form.get('subtitle')
            slug_v = request.form.get('slug')
            content_v = request.form.get('content')
            img_file_v = request.form.get('img_file')
            # writer_v = request.form.get('writer')
            # date_v=datetime.now()
        
            post=Posts.query.filter_by(sr_no=post_sr_no).first()
            post.title=title_v
            post.subtitle=subtitle_v
            post.slug=slug_v
            post.content=content_v
            post.date=post.date
            post.writer=post.writer
            post.img_file=img_file_v
            db.session.commit()
            return redirect('/edit/'+post_sr_no,)
    post=Posts.query.filter_by(sr_no=post_sr_no).first()
    return render_template('edit.html', params=params,post=post)


@app.route("/add/<string:post_sr_no>", methods=['GET','POST'])
def add_route(post_sr_no):
    if ('user' in session and session['user'] == params['admin_username']):
        if (request.method == 'POST'):
            title_v = request.form.get('title')
            subtitle_v = request.form.get('subtitle')
            slug_v = request.form.get('slug')
            content_v = request.form.get('content')
            img_file_v = request.form.get('img_file')
            writer_v = request.form.get('writer')
            date_v=datetime.now()
        
            '''sr_no, title,subtitle, slug,content, date,writer,img_file    '''
            post=Posts(title=title_v,subtitle=subtitle_v,slug=slug_v,content=content_v,date=date_v,writer=writer_v,img_file=img_file_v)
            db.session.add(post)
            db.session.commit()
    post=Posts.query.filter_by(sr_no=post_sr_no).first()
    return render_template('add.html', params=params,post_sr_no=post_sr_no,post=post)


@app.route("/delete/<string:post_sr_no>")
def delete(post_sr_no):
    if ('user' in session and session['user'] == params['admin_username']):
        # post=Posts.query.filter_by(sr_no=post_sr_no).first()
        # db.session.delete(post)
        # db.session.commit()
        pass
    return redirect('/login')

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


@app.route("/login", methods=['GET', 'POST'])
def login():
    if ('user' in session and session['user'] == params['admin_username']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if (request.method == 'POST'):
        # Admin Login
        admin_username_v = request.form.get('admin_username')
        admin_password_v = request.form.get('admin_password')
        if (admin_username_v == params['admin_username'] and admin_password_v == params['admin_password']):
            session['user'] = admin_username_v
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
            
    return render_template('login.html', params=params)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/login')


app.run(debug=True)