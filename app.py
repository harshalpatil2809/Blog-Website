from flask import Flask, render_template, url_for, redirect, session, flash
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, Regexp
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
import logging

load_dotenv()

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")
if not database_url:
    pg_host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_user = os.getenv("POSTGRES_USER", "postgres")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "")
    pg_db = os.getenv("POSTGRES_DB", "blogdb")
    database_url = f"postgresql://{pg_user}:{quote_plus(pg_pass)}@{pg_host}:{pg_port}/{pg_db}"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("APP_SECRET_KEY", "dev-secret")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy(app)

class Registration(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    user_name = StringField("username", validators=[DataRequired()])
    email = EmailField("email", validators=[
        DataRequired(),
        Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
               message="Invalid email format. Please enter a valid email.")
    ])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("submit")

    def validate_email(self, field):
        res = db.session.execute(text("SELECT 1 FROM users WHERE email = :email"), {"email": field.data})
        user = res.fetchone()
        if user:
            raise ValidationError("Email is Already taken... Please try another email.")


class LoginForm(FlaskForm):
    email = EmailField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("submit")


class Blog(FlaskForm):
    title = StringField("title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    description = StringField("disc", validators=[DataRequired()])
    submit = SubmitField("submit")


@app.route("/")
def home():
    try:
        res = db.session.execute(text("SELECT author, title, description, id FROM blogs"))
        rows = res.fetchall()
        blogs = [tuple(r) for r in rows]
        n = len(blogs)
        return render_template("index.html", blogs=blogs, n=n)
    except Exception as e:
        logger.exception("Error in home()")
        flash("Unable to load blogs right now.", "error")
        return render_template("index.html", blogs=[], n=-1), 500


@app.route("/post", methods=['POST', 'GET'])
def post():
    form = Blog()
    if form.validate_on_submit():
        if 'user_id' in session:
            user_id = session['user_id']
            title = form.title.data
            description = form.description.data
            author = form.author.data
            try:
                db.session.execute(text(
                    "INSERT INTO blogs (user_id, title, author, description) VALUES (:user_id, :title, :author, :description)"
                ), {"user_id": user_id, "title": title, "author": author, "description": description})
                db.session.commit()
                return redirect(url_for("home"))
            except Exception:
                db.session.rollback()
                logger.exception("Failed to insert blog")
                flash("Failed to save blog.", "error")
                return redirect(url_for("post"))
        else:
            flash("You must be logged in to post.", "error")
            return redirect(url_for("login"))
    return render_template("post.html", form=form)


@app.route("/login", methods=['POST', 'GET'])
def login():
    form = LoginForm()
    session.permanent = True
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            res = db.session.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
            user = res.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):
                session['user_id'] = user[0]
                return redirect(url_for("dashboard"))
            else:
                flash("Login Failed..! Please check your Email or Password.", "error")
                return redirect(url_for("login"))
        except Exception:
            logger.exception("Login error")
            flash("Login error. Try again later.", "error")
            return redirect(url_for("login"))
    return render_template("login.html", form=form)


@app.route("/registration", methods=['POST', 'GET'])
def registration():
    form = Registration()
    if form.validate_on_submit():
        name = form.name.data
        user_name = form.user_name.data
        email = form.email.data
        password = form.password.data

        hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            db.session.execute(text(
                "INSERT INTO users (name, user_name, email, password) VALUES (:name, :user_name, :email, :password)"
            ), {"name": name, "user_name": user_name, "email": email, "password": hashed_pass})
            db.session.commit()
            return redirect(url_for("login"))
        except Exception:
            db.session.rollback()
            logger.exception("Registration failed")
            flash("Registration failed. Try again later.", "error")
            return redirect(url_for("registration"))

    return render_template("register.html", form=form)


@app.route("/dashboard")
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        try:
            res = db.session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
            user = res.fetchone()
            if user:
                name = user[1]
                username = user[2]
                email = user[3]
                return render_template("dashboard.html", username=username, name=name, email=email)
        except Exception:
            logger.exception("Dashboard error")
            flash("Unable to load dashboard.", "error")
            return redirect(url_for("home"))

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have successfully Loged out...")
    return redirect(url_for("home"))


@app.route("/_dbstatus")
def _dbstatus():
    try:
        db.session.execute(text("SELECT 1"))
        return "DB OK", 200
    except Exception as e:
        logger.exception("DB connection failed")
        return f"DB ERROR: {e}", 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")