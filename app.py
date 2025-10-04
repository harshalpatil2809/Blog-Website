from flask import Flask,render_template,url_for,redirect,session,flash
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,EmailField,SubmitField
from wtforms.validators import DataRequired,Email,ValidationError,Regexp
import bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "harshalpatil@123"
app.config["MYSQL_DB"] = "blogdb"
app.secret_key = "blog-by-harshal"

mysql = MySQL(app)

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

    def validate_email(self,field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))
        user = cursor.fetchone()
        cursor.close()
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
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT author,title,description,id FROM blogs")
    blogs = cursor.fetchall()
    n = len(blogs)-1
    cursor.close()
    return render_template("index.html",blogs=blogs,n=n)


@app.route("/post", methods = ['POST','GET'])
def post():
    form  = Blog()
    if form.validate_on_submit():
        if 'user_id' in session:
            user_id = session['user_id']
            title = form.title.data
            description = form.description.data
            author = form.author.data
            cursor = mysql.connection.cursor()

            cursor.execute("INSERT INTO blogs (user_id,title, author, description) VALUES (%s, %s, %s, %s)",(user_id,title, author, description))
            mysql.connection.commit()
            cursor.close()
            
            return redirect(url_for("home"))
    return render_template("post.html",form=form)


@app.route("/login", methods = ['POST','GET'])
def login():
    form  = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        cursor = mysql.connection.cursor()

        cursor.execute(" SELECT * FROM users WHERE email = %s",(email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for("dashboard"))
        else:
            flash("Login Failed..! Please check your Email or Password.", "error")
            return redirect(url_for("login"))
        
    return render_template("login.html",form=form)


@app.route("/registration", methods=['POST','GET'])
def registration():
    form  = Registration()
    if form.validate_on_submit():
        name = form.name.data
        user_name = form.user_name.data
        email = form.email.data
        password = form.password.data

        hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor = mysql.connection.cursor()

        cursor.execute(" INSERT INTO users (name, user_name, email, password) VALUES (%s, %s, %s, %s)",(name,user_name,email,hashed_pass))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("login"))

    return render_template("register.html",form=form)



@app.route("/dashboard")
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute(" SELECT * FROM users WHERE id = %s",(user_id,))
        user = cursor.fetchone()
        cursor.close()
        if user :
            name = user[1]
            username = user[2]
            email = user[3]
            return render_template("dashboard.html", username=username, name=name, email=email)

    return redirect(url_for("login"))




@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have successfully Loged out...")
    return redirect(url_for("home"))




if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")