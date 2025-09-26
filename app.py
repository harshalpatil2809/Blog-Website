from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SECRET_KEY"] = "BLOG-by-harshal"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(200), unique = True, nullable = False)
    password = db.Column(db.String(200),  nullable = False)

class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    text = db.Column(db.Text, nullable = False)
    author = db.Column(db.String(100), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    

with app.app_context():
    db.create_all()



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/post")
def post():
    return render_template("post.html")

@app.route("/login")
def login():
    return render_template("register.html")



if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")