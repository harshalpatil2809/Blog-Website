from flask import Flask,render_template,url_for,redirect,session,flash
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,EmailField,SubmitField
from wtforms.validators import DataRequired,Email,ValidationError,Regexp
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
    discription = StringField("disc", validators=[DataRequired()])
    submit = SubmitField("submit")

    
@app.route("/")
def home():
    posts = [
    {
        "username": "Harshal",
        "title": "Getting Started with Flask",
        "description": "Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy..."
    },
    {
        "username": "Amit",
        "title": "Introduction to Python",
        "description": "Python is one of the most popular programming languages. It is simple, versatile, and widely used in web development, data science..."
    },
    {
        "username": "Sneha",
        "title": "Mastering TailwindCSS",
        "description": "TailwindCSS is a utility-first CSS framework that provides low-level utility classes. You can build modern and responsive designs..."
    },
    {
        "username": "Ravi",
        "title": "Building REST APIs with Flask",
        "description": "Learn how to build RESTful APIs with Flask by using Flask-RESTful and integrating authentication..."
    },
    {
        "username": "Pooja",
        "title": "Exploring Django vs Flask",
        "description": "Both Django and Flask are popular Python frameworks. While Django is full-featured, Flask offers flexibility and simplicity..."
    },
    {
        "username": "Kiran",
        "title": "Getting Started with React",
        "description": "React is a JavaScript library for building user interfaces. It is component-based, declarative, and widely used..."
    },
    {
        "username": "Meera",
        "title": "Database Integration with SQLAlchemy",
        "description": "SQLAlchemy is a Python SQL toolkit and ORM that allows developers to work with databases in a Pythonic way..."
    },
    {
        "username": "Aditya",
        "title": "Introduction to Machine Learning",
        "description": "Machine learning enables computers to learn from data without being explicitly programmed. Explore supervised and unsupervised learning..."
    },
    {
        "username": "Rohit",
        "title": "Git and GitHub Basics",
        "description": "Version control is crucial in software development. Learn how Git and GitHub help in collaboration and code management..."
    },
    {
        "username": "Divya",
        "title": "Mastering Bootstrap 5",
        "description": "Bootstrap 5 is a popular front-end framework that helps in building responsive and mobile-first websites quickly..."
    },
    {
        "username": "Nikhil",
        "title": "Understanding APIs",
        "description": "APIs allow applications to communicate with each other. Explore REST, GraphQL, and gRPC approaches..."
    },
    {
        "username": "Priya",
        "title": "Getting Started with Docker",
        "description": "Docker enables containerization, making applications portable and easier to deploy across different environments..."
    },
    {
        "username": "Arjun",
        "title": "Introduction to JavaScript",
        "description": "JavaScript is the backbone of web interactivity. Learn about variables, functions, DOM manipulation, and ES6 features..."
    },
    {
        "username": "Shreya",
        "title": "Data Analysis with Pandas",
        "description": "Pandas is a Python library for data manipulation and analysis. It provides data structures and functions for working with structured data..."
    },
    {
        "username": "Manish",
        "title": "Introduction to Cloud Computing",
        "description": "Cloud computing delivers computing services like servers, storage, and databases over the internet..."
    },
    {
        "username": "Aishwarya",
        "title": "Getting Started with Vue.js",
        "description": "Vue.js is a progressive JavaScript framework used to build user interfaces. It is lightweight and easy to integrate..."
    },
    {
        "username": "Siddharth",
        "title": "Python for Data Science",
        "description": "Python provides powerful libraries like NumPy, Pandas, and Matplotlib that make data analysis and visualization easy..."
    },
    {
        "username": "Neha",
        "title": "Building Responsive Websites",
        "description": "Responsive design ensures websites work well on all screen sizes. Learn about media queries and mobile-first design..."
    },
    {
        "username": "Varun",
        "title": "Understanding Artificial Intelligence",
        "description": "Artificial Intelligence is the simulation of human intelligence by machines. Explore its applications and future possibilities..."
    },
    {
        "username": "Isha",
        "title": "Getting Started with Node.js",
        "description": "Node.js is a runtime environment that allows JavaScript to run on the server. Learn about npm and asynchronous programming..."
    },
    {
        "username": "Kabir",
        "title": "Mastering CSS Grid and Flexbox",
        "description": "CSS Grid and Flexbox are powerful layout systems that simplify the process of building responsive designs..."
    },
    {
        "username": "Tanvi",
        "title": "Working with RESTful APIs",
        "description": "RESTful APIs are widely used in web applications. Learn how to consume and build them with different programming languages..."
    },
    {
        "username": "Rahul",
        "title": "Getting Started with PostgreSQL",
        "description": "PostgreSQL is a powerful open-source relational database system. Learn how to install, configure, and run queries..."
    }
]

    return render_template("index.html", posts=posts)


@app.route("/post")
def post():
    return render_template("post.html")


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
        print(user)
        if user :
            name = user[1]
            username = user[2]
            email = user[3]
            return render_template("dashboard.html", username=username)

    return redirect(url_for("login"))




@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have successfully Loged out...")
    return redirect(url_for("home"))




if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")