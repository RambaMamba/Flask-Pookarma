from Pookarma.models import User, Post
from flask import render_template, url_for, flash, redirect, request
from Pookarma.forms import RegistrationForm, LoginForm,UpdateAccountForm, PostForm
from Pookarma import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf.file import FileField
from werkzeug.utils import secure_filename
import os
import urllib.request



@app.route("/post/feed")
@app.route("/")
@app.route("/feed")
def feed():
    posts = Post.query.all()
    return render_template('feed.html', posts = posts)

@app.route("/post/leaderboard")
@app.route("/leaderboard")
def leaderboard():
    users = User.query.all()
    userDict = {}
    for user in users:
        userDict[user.username] = user.karma
    sort = sorted(userDict.items(), key=lambda x: x[1], reverse=True)
    
    finalLeader = []
    for people in sort:
        finalLeader.append(User.query.filter_by(username = people[0]).first())
    

    return render_template('leaderboard.html', topUsers = finalLeader)

@app.route('/post/about', methods=['GET', 'POST'])
@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route('/post/register', methods=['GET', 'POST'])
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password= hashed_password, karma = 0)
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('feed'))
    return render_template('register.html', title='Register', form=form)

@app.route('/post/login', methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('feed'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
@app.route('/post/logout')

def logout():
    logout_user()
    flash('Logout success!')
    return redirect(url_for('feed'))

@app.route("/account", methods=['GET', 'POST'])
@app.route('/post/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account Has Been Updated!', 'success')
        return redirect(url_for('account'))
    else :
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file = image_file, form = form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    print("function started")
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, author = current_user)
        db.session.add(post)
        current_user.karma += 1
        db.session.commit()
        str123 = "You now have " + str(current_user.karma) +" karma points!"
        flash(str123, 'success')
        flash('Your post has been created!', 'success')
        return redirect(url_for('feed'))
    return render_template('create_post.html', title='New Post', form = form)
