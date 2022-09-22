'''Flask app for Feedback'''

from flask import Flask, request, render_template
from models import db, connect_db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'oh-so-secret'

connect_db(app)

@app.route('/')
def root():
    '''Redirect to /register.'''

    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def create_user():
    '''Form to register new user, and handle adding.'''

    form = RegisterForm()

    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != 'csrf_token'}
        new_user = User.register(**data)

        db.session.add(new_user)
        db.session.commit()

        session['username'] = new_user.username  # keep logged in

        flash(f'Welcome to the Feedback App, {new_user.first_name}!')
        return redirect('/secret')
    
    else:
        return render_template('register.html', form=form)
    
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    '''Form to login existing user, and handle authenticating.'''

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username  # keep logged in
            return redirect('/secret')

        else:
            form.username.errors = ['Username or password is incorrect.']

    return render_template('login.html', form=form)

@app.route('/secret')
def secret():

    if 'username' not in session:
        flash('You must be logged in to view!')
        return redirect('/')

    else:
        return render_template('secret.html')