from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import bcrypt, db
from flaskblog.users.forms  import (UserRegistration, UserLogin, UpdateAccount,
                             PasswordRequestForm, PasswordResetForm)
from flaskblog.models import User, Post
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users',__name__)

@users.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        print(f'current user is {current_user}')
        return redirect(url_for('main.home'))
    form = UserRegistration()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully, Please login', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='register', form=form)


@users.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        print(f'current user is {current_user}')
        return redirect(url_for('main.home'))
    form = UserLogin()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash(f'Login is not successful, Please try again with correct credentials', 'danger')
    return render_template('login.html', title='login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateAccount()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_pic = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account updated successfully','success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.profile_pic)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route('/user/<string:username>')
def user_posts(username):
    # name = request.args.get("name", "World")
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(per_page=5, page=page)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route('/password_request', methods=['GET', 'POST'])
def password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = PasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('password reset link has been sent to your mail successfully', 'info')
        return redirect(url_for('users.login'))
    return render_template('password_request.html', title='Password Reset', form=form)


@users.route('/password_request/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.validate_reset_token(token)
    if user is None:
        flash('Invalid or expired token, Kindly try again', 'warning')
        return redirect(url_for('users.password_request'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password has been updated', 'success')
        return redirect(url_for('users.login'))
    return render_template('password_reset.html', form=form, title='Password Reset')