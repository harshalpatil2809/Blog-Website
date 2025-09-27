from flask import Flask,render_template,url_for,redirect,session,flash
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,EmailField,SubmitField
from wtforms.validators import DataRequired,Email,ValidationError
import bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "harshalpatil@123"
app.config["MYSQL_DB"] = "blogdb"
app.secret_key = "blog-by-harshal"

mysql = MySQL(app)

class Registration(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    email = EmailField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("submit")

class LoginForm(FlaskForm):
    email = EmailField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("submit")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/post")
def post():
    return render_template("post.html")

@app.route("/login")
def login():
    form  = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        

        cursor = mysql.connection.cursor()

        cursor.execute(" SELECT * FROM users WHERE email = %s"(email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encod('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for("dashboard"))
        else:
            flash("Login Failed..!, Please check your Email or Password.")
            return redirect(url_for("login"))


@app.route("/registration", methods=['POST','GET'])
def registration():
    form  = Registration()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor = mysql.connection.cursor()

        cursor.execute(" INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",(name,email,hashed_pass))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("login"))

    return render_template("register.html",form=form)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")