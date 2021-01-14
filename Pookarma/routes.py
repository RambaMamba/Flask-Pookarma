from Pookarma.models import User, Post
from flask import render_template, url_for, flash, redirect, request
from Pookarma.forms import RegistrationForm, LoginForm
from Pookarma import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required





posts1 = ["Post at 7:19 Jan 13 by user ShreyBirmiwal: DooDooKarma has released!", "Post at 7:10 Jan 13 by user ShreyBirmiwal: Picking up poo at balcones!", "Post at 7:19 Jan 13 by user ShreyBirmiwal: Dog Meetup in austin anyone?"]

@app.route("/")
@app.route("/feed")
def feed():
    return render_template('feed.html', posts = posts1)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password= hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('feed'))
    return render_template('register.html', title='Register', form=form)


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
def logout():
    logout_user()
    flash('Logout success!')
    return redirect(url_for('feed'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')
