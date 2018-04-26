from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
import cgi


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:puppies@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'puppups'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'mainpage', 'static']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/register', methods=['POST', 'GET'])
def register():
    verror = ""
    derror = ""
    if request.method == 'POST':
        email = cgi.escape(request.form['email'])
        password = cgi.escape(request.form['password'])
        verify = cgi.escape(request.form['verify'])

       
        if password != verify:
            verror = "Your passwords do not match."
            return render_template('register.html', verror=verror)
        existing_user = User.query.filter_by(email=email).first()

        
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            derror = "This email is already in use."
            return render_template('register.html', derror=derror)

    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = cgi.escape(request.form['email'])
        password = cgi.escape(request.form['password'])
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged on")
            print(session)
            return redirect('/')
        else: 
            flash('User Password incorrect, or user does not exist', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route('/blogpage', methods=['POST', 'GET'])
def blogpage():
    blog_id=int(request.args.get('blog-id'))
    blog = Blog.query.get(blog_id)
    return render_template('blogpage.html', blog=blog)


@app.route('/users', methods=['POST', 'GET'])
def users():
    users = User.query.filter_by().all()
    return render_template('userpage.html', users=users)


@app.route('/user', methods=['POST', 'GET'])
def user():
    user_id=(request.args.get('user-id'))
    blogs = Blog.query.filter_by(owner_id=user_id).all()
    return render_template('user.html', blogs=blogs)


@app.route('/', methods=['POST', 'GET'])
def index():
    owner = User.query.filter_by(email=session['email']).first()
    blogs = Blog.query.filter_by(owner=owner).all()
    
    return render_template('bloglist.html',title="bloglist", blogs=blogs)


@app.route('/mainpage', methods=['POST', 'GET'])
def mainpage():
    blogs = Blog.query.filter_by().all()
    return render_template('mainpage.html',title="Mainpage", blogs=blogs)


@app.route('/addablog', methods=['POST', 'GET'])
def addablog():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        if not request.form['title'] or not request.form['body']:
            post_error = "Your body or title is blank!"
            return render_template('addablog.html', post_error=post_error)
        blog_title = cgi.escape(request.form['title'])
        blog_body = cgi.escape(request.form['body'])

        
        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()
        blog = Blog.query.filter_by(owner=owner).order_by(desc(Blog.id)).first()
        return render_template('blogpage.html', blog=blog)
    return render_template('addablog.html', title="Add a blog!")


if __name__ == '__main__':
    app.run()