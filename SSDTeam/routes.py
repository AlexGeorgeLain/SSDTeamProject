from ssdteam.models import User, Post, BloodPressure, Weight
from flask import render_template, url_for, flash, redirect, request, abort, after_this_request
from ssdteam.forms import RegistrationForm, LoginForm, PostForm, BloodPressureForm, WeightForm
from ssdteam import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from cryptography.fernet import Fernet
from ssdteam.encryption import encrypt_medical_record, decrypt_medical_record, encrypt_post, decrypt_post
from ssdteam.downloads import download_record
import os


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        encrypted_content = Post.query.filter_by(recipient=current_user.email).order_by(Post.date_posted.desc())

        posts = decrypt_post(encrypted_content, current_user.key)

        return render_template('home.html', posts=posts, title='Home')
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login failed", 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():

        encrypted_content = encrypt_post(form.content.data, form.recipient.data)

        post = Post(recipient=form.recipient.data, title=form.title.data, content=encrypted_content, author=current_user)
        db.session.add(post)
        db.session.commit()

        flash('Post created.', 'success')
        return redirect(url_for('home'))

    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/bloodpressure", methods=['GET', 'POST'])
@login_required
def blood_pressure():
    form = BloodPressureForm()
    if form.validate_on_submit():
        encrypted_blood_pressure = encrypt_medical_record(form.blood_pressure.data, current_user.key)

        bp = BloodPressure(record=encrypted_blood_pressure, user_id=current_user.id)
        db.session.add(bp)
        db.session.commit()

        flash('Blood pressure submitted.', 'success')
        return redirect(url_for('blood_pressure'))

    return render_template('blood_pressure.html', title='New Entry', form=form, legend='New Blood Pressure')


@app.route("/weight", methods=['GET', 'POST'])
@login_required
def weight():
    form = WeightForm()
    if form.validate_on_submit():
        encrypted_weight = encrypt_medical_record(form.weight.data, current_user.key)
        weight_new = Weight(record=encrypted_weight, user_id=current_user.id)
        db.session.add(weight_new)
        db.session.commit()

        flash('Weight submitted.', 'success')
        return redirect(url_for('weight'))
    return render_template('weight.html', title='New Entry', form=form, legend='New Weight')


@app.route("/astronauts")
@login_required
def astronauts():
    if current_user.is_authenticated:
        posts = User.query.filter_by(role='Astronaut').all()

        return render_template('astronauts.html', posts=posts, title='Astronauts')
    else:
        return redirect(url_for('login'))


@app.route("/accounts/<string:email>/bloodpressure")
@login_required
def astronauts_blood_pressure(email):
    if current_user.is_authenticated:
        user = User.query.filter_by(email=email).first()
        user_id = user.id
        encrypted_bp = BloodPressure.query.filter_by(user_id=user_id).all()

        posts = decrypt_medical_record(encrypted_bp, User.query.filter_by(email=email).first().key)

        return render_template('single_medical_record.html', posts=posts, user=user, title='Blood Pressure')
    else:
        return redirect(url_for('login'))


@app.route("/accounts/<string:email>/weight")
@login_required
def astronauts_weight(email):
    if current_user.is_authenticated:
        user = User.query.filter_by(email=email).first()
        user_id = user.id
        encrypted_weight = Weight.query.filter_by(user_id=user_id).all()

        posts = decrypt_medical_record(encrypted_weight, User.query.filter_by(email=email).first().key)

        return render_template('single_medical_record.html', posts=posts, user=user, title='Weight')
    else:
        return redirect(url_for('login'))


@app.route("/accounts/<string:email>/posts")
@login_required
def user_posts(email):
    if current_user.is_authenticated:
        user = User.query.filter_by(email=email).first()
        encrypted_posts = db.session.query(Post)\
            .where(((Post.user_id == user.id) & (Post.recipient == current_user.email))
                   | ((Post.user_id == current_user.id) & (Post.recipient == user.email)))\
            .order_by(Post.date_posted.desc()).all()

        posts = []

        for post in encrypted_posts:
            post_list = [post]
            if post_list[0].recipient == current_user.email:
                posts.append(decrypt_post(post_list, current_user.key)[0])

            if post_list[0].recipient == user.email:
                posts.append(decrypt_post(post_list, user.key)[0])

        return render_template('user_posts.html', posts=posts, user=user, title='Posts')
    else:
        return redirect(url_for('login'))


@app.route("/accounts/<string:email>/<string:record_type>/download")
@login_required
def download_data(email, record_type):

    @after_this_request
    def delete_file(response):
        os.remove('ExportedData.csv')
        return response

    return download_record(email, record_type)


@app.route("/accounts/<string:email>",  methods=['GET', 'POST'])
@login_required
def user_account(email):
    user = User.query.filter_by(email=email).first()

    return render_template('user_account.html', user=user, title='Account')


@app.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    if current_user.role != 'Admin':
        abort(403)

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data, last_name=form.last_name.data,
                    email=form.email.data, password=hashed_password, key=Fernet.generate_key().decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.first_name.data} {form.last_name.data}.', 'success')
        return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form)


@app.route("/user/<string:email>/delete", methods=['POST'])
@login_required
def delete_user(email):
    if current_user.role == 'Admin':
        user = User.query.filter_by(email=email).first()
        posts_received = Post.query.filter_by(recipient=user.email).all()
        posts = Post.query.filter_by(user_id=user.id).all()
        blood_pressures = BloodPressure.query.filter_by(user_id=user.id).all()
        weights = Weight.query.filter_by(user_id=user.id).all()

        for weight in weights:
            db.session.delete(weight)

        for bp in blood_pressures:
            db.session.delete(bp)

        for post in posts:
            db.session.delete(post)

        for post in posts_received:
            db.session.delete(post)

        db.session.delete(user)

        db.session.commit()
        flash('User deleted.', 'success')
        return redirect(url_for('astronauts'))

    else:
        return redirect(url_for('home'))


@app.route("/account",  methods=['GET', 'POST'])
@login_required
def account():
    return render_template('account.html', title='My Account')


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
