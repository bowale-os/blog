from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, g, session
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
load_dotenv()

# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from functools import wraps


def admin_only(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if not (current_user.is_authenticated and current_user.id == 1):
            abort(403)
        return func(*args, **kwargs)
    return decorated


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET")
ckeditor = CKEditor(app)
Bootstrap5(app)

# LOGGED_IN INJECTOR
@app.context_processor
def inject_logged_in():
    return dict(logged_in = session.get('logged_in', False))


# CREATE DATABASE
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# TODO: Configure Flask-Login for authentication
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CONFIGURE TABLES' SCHEMA
# Parent table with one-to-many relationship with blogposts
# TODO: Create a User table for all your registered users. with usermixin

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="commenter")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    author_id : Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

    comments = relationship("Comment", back_populates="post")

class Comment(db.Model):
    __tablename__ = "blog_comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    post = relationship("BlogPost", back_populates="comments")

    commenter_id : Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    commenter =  relationship("User", back_populates="comments")

with app.app_context():
    db.create_all()


#CREATE SPECIFIC ROUTES
#Home_page
@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    print(f"loaded posts {posts}")
    return render_template("xinde.html", all_posts=posts)


# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["POST", "GET"])
def register():
    form  = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            flash(f"Log in with {email}")
            return redirect(url_for('login'))

        hashed_and_salted = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        user = User(name=name, email=email, password=hashed_and_salted)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        session['logged_in'] = True
        return redirect(url_for('get_all_posts'))

    return render_template("register.html", form=form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email ==  email))
        user = result.scalar()
        if not user:
            flash("Wrong email. Email is not tied to any account!")
            return redirect(url_for('login'))

        if check_password_hash(user.password, password):
            login_user(user)
            session['logged_in'] = True
            return redirect(url_for('get_all_posts'))
        else:
            flash("Error: Incorrect details entered...")
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    session['logged_in'] = False
    return redirect(url_for('get_all_posts'))




# TODO: Allow logged-in users to comment on posts
@login_required
@app.route("/post/<int:post_id>", methods = ["POST", "GET"])
def show_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    form =  CommentForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to log in to comment.")
            return redirect(url_for('login'))

        new_comment = Comment(
            content = form.comment.data,
            commenter = current_user,
            post = post
        )

        db.session.add(new_comment)
        db.session.commit()
        flash("Your comment has been posted")
        return redirect(url_for('show_post', post_id=post_id))


    return render_template("post.html", post=post, form=form)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")



message_dict = {}
#monitor and respond to enquiries
email_recipient = os.getenv("email_recipient")
APP_PASSWORD = os.getenv("APP_PASSWORD")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    from flask import request
    post_method = request.method
    match post_method:
        case "POST":
            print('ok post')
            name = request.form['name']
            email = request.form['email']
            number = request.form['phone']
            message = request.form['message']
            message_dict[name] = {'email': email, 'number': number, 'message': message}

            subject = 'Blog Contact Form Submission'
            body = F"""{name} says: \n""" + message_dict[name]['message']

            message = MIMEMultipart()
            message['From'] = email
            message['To'] = email_recipient
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email, APP_PASSWORD)
                server.sendmail(email, email_recipient, message.as_string())
                msg_sent = True
                print('Emails sent!!')

            except Exception as e:
                print(f'error {e} occured')
            finally:
                server.quit()


        case "GET":
            return render_template("contact.html")
    return render_template("contact.html", msg_sent = msg_sent)


if __name__ == "__main__":
    app.run(debug=True, port=5002)
