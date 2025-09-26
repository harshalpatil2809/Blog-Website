from flask import Flask,render_template,url_for,redirect
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,EmailField,SubmitField
from wtforms.validators import DataRequired,Email,ValidationError
import bcrypt
from flask_mysqldb import MYSQL

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "harshalpatil@123"
app.config["MYSQL_DB"] = "blogdb"
app.secret_key = "blog-by-harshal"

mysql = MYSQL(app)

class Registration(FlaskForm):
    name = StringField("Name", DataRequired())
    email = EmailField("Email", DataRequired(), Email())
    password = PasswordField("password", DataRequired())
    submit = SubmitField("submit")


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/post")
def post():
    return render_template("post.html")

@app.route("/registration")
def registration():
    form  = Registration()
    if form.validate_on_submit:
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_pass = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

        cursor = MYSQL.connection.cursor()

        cursor.execute(" INSERT INTO (name,email,password) VALUES (%s,%s,%s)",(name,email,password))
        mysql.connect.commit()
        cursor.close()

        return redirect(url_for("login"))

    return render_template("register.html")



if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")