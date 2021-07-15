"""Module containing the routes for the web app.

Functions:
    home -- loads the user homepage containing all posts involving the user.
    login -- loads the user log in page.
    logout -- logs out the user.
    new_post -- loads page for creating a new post.
    blood_pressure -- loads page for creating new blood pressure record.
    weight -- loads page for creating new weight record.
    astronauts -- loads page showing all astronauts.
    astronauts_blood_pressure -- loads page showing all blood pressure records
    for a given astronaut.
    astronauts_weight -- loads page showing all weight records for a given astronaut.
    user_posts -- loads page showing all posts between the current user and a given user.
    download_data -- downloads the records on a given page.
    user_account -- loads page for a given user and all posts between them and the current user.
    register -- loads page for an admin to register a new user
    delete_user -- allows an admin to delete a user.
    account -- loads page to view the current user's account info.
    users -- loads page listing all users if the current user is an admin.

"""

import os
from flask import render_template, url_for, flash, redirect, request, abort, after_this_request
from flask_login import login_user, current_user, logout_user, login_required
from cryptography.fernet import Fernet
from ssdteam import app, db, bcrypt
from ssdteam.models import User, Post, BloodPressure, Weight, delete_user_from_db
from ssdteam.forms import RegistrationForm, LoginForm, \
    PostForm, BloodPressureForm, WeightForm

from ssdteam.encryption import encrypt_medical_record,\
    decrypt_medical_record, encrypt_post, decrypt_post

from ssdteam.downloads import download_record


@app.route("/")
@app.route("/home")
def home():
    """
    Loads home page with all post to and from the current user.
    If user isn't authenticated the n redirects to login page.
    """

    if current_user.is_authenticated:
        encrypted_posts = db.session.query(Post) \
            .where((Post.recipient == current_user.email) | (Post.user_id == current_user.id))\
            .order_by(Post.date_posted.desc()).all()

        posts = []

        for encrypted_post in encrypted_posts:
            post_list = [encrypted_post]
            if post_list[0].recipient == current_user.email:
                posts.append(decrypt_post(post_list, current_user.key)[0])

            else:
                user = User.query.filter_by(email=encrypted_post.recipient).first()
                posts.append(decrypt_post(post_list, user.key)[0])

        return render_template('home.html', posts=posts, title='Home')

    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    User login page.
    Redirects to page the user was trying to access once authenticated.
    If login route was initial request then redirects to home.
    """

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('home'))

        flash("Login failed", 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    """Logs out current user and redirects to login page."""
    logout_user()
    return redirect(url_for('login'))


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    """
    New post page.
    Takes the submitted PostForm, encrypts the content and saves it to the database.
    """

    form = PostForm()
    if form.validate_on_submit():

        encrypted_content = encrypt_post(form.content.data, form.recipient.data)

        encrypted_post = Post(recipient=form.recipient.data, title=form.title.data,
                              content=encrypted_content, author=current_user)

        db.session.add(encrypted_post)
        db.session.commit()

        flash('Post created.', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/bloodpressure", methods=['GET', 'POST'])
@login_required
def blood_pressure():
    """
    Loads page for astronaut to submit new blood pressure record.
    Takes data from the submitted BloodPressure form, encrypts it,
    and saves it to the database.
    """

    form = BloodPressureForm()
    if form.validate_on_submit():
        encrypted_blood_pressure = encrypt_medical_record(form.blood_pressure.data,
                                                          current_user.key)

        bp = BloodPressure(record=encrypted_blood_pressure, user_id=current_user.id)
        db.session.add(bp)
        db.session.commit()

        flash('Blood pressure submitted.', 'success')
        return redirect(url_for('blood_pressure'))

    encrypted_bp = BloodPressure.query. \
        filter_by(user_id=current_user.id).order_by(BloodPressure.date_posted.desc()).all()

    posts = decrypt_medical_record(encrypted_bp,
                                   current_user.key)

    return render_template('blood_pressure.html', title='Blood Pressure',
                           form=form, posts=posts,  legend='New Blood Pressure')


@app.route("/weight", methods=['GET', 'POST'])
@login_required
def weight():
    """
    Loads page for astronaut to submit new weight record.
    Takes data from the submitted Weight form, encrypts it,
    and saves it to the database.
    """

    form = WeightForm()
    if form.validate_on_submit():
        encrypted_weight = encrypt_medical_record(form.weight.data, current_user.key)
        weight_new = Weight(record=encrypted_weight, user_id=current_user.id)
        db.session.add(weight_new)
        db.session.commit()

        flash('Weight submitted.', 'success')
        return redirect(url_for('weight'))

    encrypted_weight = Weight.query.filter_by(user_id=current_user.id). \
        order_by(Weight.date_posted.desc()).all()

    posts = decrypt_medical_record(encrypted_weight,
                                   current_user.key)

    return render_template('weight.html', title='Weight', posts=posts, form=form, legend='New Weight')


@app.route("/astronauts")
@login_required
def astronauts():
    """
    Loads a page that displays all the current astronauts in the database,
    providing the  current user has the required role.

    """

    if current_user.role in ['Admin', 'Medic']:
        posts = User.query.filter_by(role='Astronaut').all()

        return render_template('users_list.html', posts=posts, title='Astronauts')

    return abort(403)


@app.route("/accounts/<string:email>/bloodpressure")
@login_required
def astronauts_blood_pressure(email):
    """
    Loads page displaying the blood pressure records of a given astronaut,
    proving that the current user has the correct role

    Keyword args:
        email -- email of the astronaut whose records are being viewed.
    """

    if current_user.role in ['Admin', 'Medic'] \
            or current_user.email == email:

        user = User.query.filter_by(email=email).first()
        user_id = user.id
        encrypted_bp = BloodPressure.query.\
            filter_by(user_id=user_id).order_by(BloodPressure.date_posted.desc()).all()

        posts = decrypt_medical_record(encrypted_bp,
                                       User.query.filter_by(email=email).first().key)

        return render_template('single_medical_record.html', posts=posts,
                               user=user, title='Blood Pressure')

    return redirect(url_for('login'))


@app.route("/accounts/<string:email>/weight")
@login_required
def astronauts_weight(email):
    """
    Loads page displaying the weight records of a given astronaut,
    proving that the current user has the correct role.

    Keyword args:
        email -- email of the astronaut whose records are being viewed.
    """

    if current_user.role in ['Admin', 'Medic'] \
            or current_user.email == email:

        user = User.query.filter_by(email=email).first()
        user_id = user.id
        encrypted_weight = Weight.query.filter_by(user_id=user_id).\
            order_by(Weight.date_posted.desc()).all()

        posts = decrypt_medical_record(encrypted_weight,
                                       User.query.filter_by(email=email).first().key)

        return render_template('single_medical_record.html', posts=posts, user=user, title='Weight')

    return redirect(url_for('login'))


@app.route("/accounts/<string:email>/posts")
@login_required
def user_posts(email):
    """
    Loads page displaying all posts between a given user
    and the current user.

    Keyword args:
        email -- email of the user whose posts are being viewed.
    """

    if current_user.is_authenticated:
        user = User.query.filter_by(email=email).first()
        encrypted_posts = db.session.query(Post)\
            .where(((Post.user_id == user.id) & (Post.recipient == current_user.email))
                   | ((Post.user_id == current_user.id) & (Post.recipient == user.email)))\
            .order_by(Post.date_posted.desc()).all()

        posts = []

        for encrypted_post in encrypted_posts:
            post_list = [encrypted_post]
            if post_list[0].recipient == current_user.email:
                posts.append(decrypt_post(post_list, current_user.key)[0])

            if post_list[0].recipient == user.email:
                posts.append(decrypt_post(post_list, user.key)[0])

        return render_template('user_posts.html', posts=posts, user=user, title='Posts')

    return redirect(url_for('login'))


@app.route("/accounts/<string:email>/<string:record_type>/download")
@login_required
def download_data(email, record_type):
    """
    Downloads the record being viewed, provided current user is the record owner,
    or the current user has the appropriate role.

    Keyword args:
        email -- email of the owner of the records.
        record_type -- record type to be downloaded.
    """

    @after_this_request
    def delete_file(response):
        os.remove('ExportedData.csv')
        return response

    if current_user.email == email or \
            current_user.role in ['Admin', 'Medic']:
        return download_record(email, record_type)

    return abort(403)


@app.route("/accounts/<string:email>", methods=['GET', 'POST'])
@login_required
def user_account(email):
    """
    Loads the specified user account info, along with the post between
    them and the current user.

    Keyword args:
        email -- email address of the user account to be viewed
    """

    user = User.query.filter_by(email=email).first()
    encrypted_posts = db.session.query(Post) \
        .where(((Post.user_id == user.id) & (Post.recipient == current_user.email))
               | ((Post.user_id == current_user.id) & (Post.recipient == user.email))) \
        .order_by(Post.date_posted.desc()).all()

    posts = []

    for encrypted_post in encrypted_posts:
        post_list = [encrypted_post]
        if post_list[0].recipient == current_user.email:
            posts.append(decrypt_post(post_list, current_user.key)[0])

        if post_list[0].recipient == user.email:
            posts.append(decrypt_post(post_list, user.key)[0])

    return render_template('user_account.html', user=user, posts=posts, title='Account')


@app.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    """
    Loads page for registering new user, providing the current user is an admin.
    Once the form is submitted, the password is hashed, and the user account
    information is saved into the database.
    """
    if current_user.role != 'Admin':
        abort(403)

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    password=hashed_password,
                    key=Fernet.generate_key().decode('utf-8'))

        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.first_name.data} {form.last_name.data}.', 'success')
        return redirect(url_for('register'))

    return render_template('register.html', title='Register', form=form)


@app.route("/user/<string:email>/delete", methods=['POST'])
@login_required
def delete_user(email):
    """
    Deletes a user from the database, along with their associated data.

    Keyword args:
        email -- email of the user account to be deleted
    """

    if current_user.role == 'Admin':
        delete_user_from_db(email)
        flash('User deleted.', 'success')

        return redirect(url_for('users'))

    return abort(403)


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    """
    Loads page showing the account info of the current user.
    """

    return render_template('account.html', title='My Account')


@app.route("/users")
@login_required
def users():
    """
    Loads a list of all registered user if the current user is an admin.
    """

    if current_user.role == 'Admin':
        all_users = User.query.all()

        return render_template('users_list.html', posts=all_users, title='Users')

    return abort(403)


@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form. content.data
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('home'))
