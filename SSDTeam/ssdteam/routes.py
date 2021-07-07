from ssdteam.models import User, Post, BloodPressure
from flask import render_template, url_for, flash, redirect, request, abort
from ssdteam.forms import RegistrationForm, LoginForm, PostForm, BloodPressureForm, WeightForm
from ssdteam import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(recipient=current_user.email).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template('home.html', posts=posts, title='Home')
    else:
        return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    if current_user.role != 'Admin':
        abort(403)

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.first_name.data} {form.last_name.data}.', 'success')
        return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login failed", 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account",  methods=['GET', 'POST'])
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(recipient=form.recipient.data, title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


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


@app.route("/user/<string:email>")
@login_required
def user_posts(email):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(email=email).first_or_404()
    posts = Post.query.filter_by(author=user, recipient=current_user.email).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@app.route("/bloodpressure", methods=['GET', 'POST'])
@login_required
def blood_pressure():
    form = BloodPressureForm()
    if form.validate_on_submit():
        bp = BloodPressure(blood_pressure=form.blood_pressure.data, user_id=current_user.id)
        db.session.add(bp)
        db.session.commit()
        flash('Blood pressure submitted.', 'success')
        return redirect(url_for('home'))
    return render_template('blood_pressure.html', title='New Entry', form=form, legend='New Blood Pressure')


@app.route("/weight", methods=['GET', 'POST'])
@login_required
def weight():
    form = WeightForm()
    if form.validate_on_submit():
        bp = WeightForm(weight=form.weight.data, user_id=current_user.id)
        db.session.add(bp)
        db.session.commit()
        flash('Blood pressure submitted.', 'success')
        return redirect(url_for('home'))
    return render_template('weight.html', title='New Entry', form=form, legend='New Weight')