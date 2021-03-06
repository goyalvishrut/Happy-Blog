from distutils.sysconfig import customize_compiler
from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import math
from flask_mail import Mail
import json
from slugify import slugify,Slugify,UniqueSlugify
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
    posts = Posts.query.order_by(Posts.date.desc()).all()
    last=math.ceil(len(posts)/int(params['numbers_of_posts']))
    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['numbers_of_posts']):(page-1)*int(params['numbers_of_posts'])+int(params['numbers_of_posts'])]
    # page=request.args.get('page')
    '''pagination'''
    #first page
    if(page==1):
        prev="#"
        next="/?page="+str(page+1)
    #last
    elif(page==last):
        prev="/?page="+str(page-1)
        next="#"   
    #middle
    else:
        prev="/?page="+str(page-1)
        next="/?page="+str(page+1)



    # posts = Posts.query.all()[0:params['numbers_of_posts']]
    return render_template('index.html', params=params, posts=posts,prev=prev,next=next)


@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/uploader", methods=['GET', 'POST'])
def uploader(post_slug,upload_type):
    if ('user' in session and session['user'] == params['admin_username']):
        if request.method == 'POST':
            f=request.files['file1']
            if f.filename=="" and upload_type=="add_upload":
                return params['default_post_bg_img']
            if f.filename=="" and upload_type=="edit_upload":
                return None
            f_name=post_slug+".jpg"
            f.save(os.path.join(app.config['UPLOADER_PATH'],secure_filename(f_name)))
            return f_name
            

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/edit/<string:post_sr_no>", methods=['GET','POST'])
def edit_route(post_sr_no):
    custom_slugify = UniqueSlugify(to_lower=True)
    if ('user' in session and session['user'] == params['admin_username']):
        if (request.method == 'POST'):
            title_v = request.form.get('title')
            subtitle_v = request.form.get('subtitle')
            # slug_v = request.form.get('slug')
            content_v = request.form.get('content')
            # img_file_v = request.form.get('img_file')
            # writer_v = request.form.get('writer')
            # date_v=datetime.now()
        
            post=Posts.query.filter_by(sr_no=post_sr_no).first()
            slug_v=(custom_slugify(title_v+str(post.sr_no)))
            img_v_temp=uploader(slug_v,"edit_upload")
            if(img_v_temp==None):
                img_file_v=post.img_file
            else:
                img_file_v = img_v_temp
            post.title=title_v
            post.subtitle=subtitle_v
            post.slug=slug_v
            post.content=content_v
            post.date=post.date
            post.writer=post.writer
            post.img_file=img_file_v
            db.session.commit()
            post = Posts.query.filter_by(slug=slug_v).first()
            return redirect('/post/'+slug_v)
    post=Posts.query.filter_by(sr_no=post_sr_no).first()
    return render_template('edit.html', params=params,post=post)


@app.route("/add/0", methods=['GET','POST'])
def add_route():
    if ('user' in session and session['user'] == params['admin_username']):
        if (request.method == 'POST'):

            custom_slugify = UniqueSlugify(to_lower=True)
            title_v = request.form.get('title')
            subtitle_v = request.form.get('subtitle')
            # slug_v = request.form.get('slug')
            content_v = request.form.get('content')
            writer_v = request.form.get('writer')
            date_v=datetime.now()
            post = Posts.query.filter_by().all()

            slug_v=(custom_slugify(title_v+str(post[-1].sr_no+1)))
            img_file_v = uploader(slug_v,"add_upload")
            '''sr_no, title,subtitle, slug,content, date,writer,img_file    '''
            post=Posts(title=title_v,subtitle=subtitle_v,slug=slug_v,content=content_v,date=date_v,writer=writer_v,img_file=img_file_v)
            db.session.add(post)
            db.session.commit()

            return redirect('/post/'+slug_v)
        return render_template('add.html', params=params)
    else:
        return render_template('login.html',params=params)


@app.route("/delete/<string:post_sr_no>")
def delete(post_sr_no):
    if ('user' in session and session['user'] == params['admin_username']):
        post=Posts.query.filter_by(sr_no=post_sr_no).first()
        db.session.delete(post)
        db.session.commit()
        if(post.img_file!=params['default_post_bg_img']):
            os.remove(os.path.join(app.config['UPLOADER_PATH'],post.img_file))
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
        # mail.send_message('New message from ' + name_v + ' (HAPPY BLOG)',
        #                   sender=email_v,
        #                   recipients=[params['gmail_user']],
        #                   body=message_v + "\n" + phone_v)
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