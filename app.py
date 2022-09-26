'''Flask app for Feedback'''

from flask import Flask, render_template, redirect, session, flash
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, AddFeedbackForm, UpdateFeedbackForm

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
        # username = form.username.data
        # password = form.password.data
        # email = form.email.data
        # first_name = form.first_name.data
        # last_name = form.last_name.data

        # new_user = User.register(username=username, password=password, email=email, first_name=first_name, last_name=last_name)

        db.session.add(new_user)
        db.session.commit()

        session['current_user'] = new_user.username  # keep logged in

        flash(f'Welcome to the Feedback App, {new_user.first_name}!')
        return redirect(f'/users/{session["current_user"]}')
    
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
            session['current_user'] = user.username  # keep logged in
            return redirect(f'/users/{session["current_user"]}')

        else:
            form.username.errors = ['Username or password is incorrect.']

    return render_template('login.html', form=form)

@app.route('/secret')
def secret():
    '''The secret page for registered users, only!'''

    if 'current_user' not in session:
        flash('You must be logged in to view this page!')
        return redirect('/')

    else:
        flash('This was the old destination after registering or logging in. You were not expected to find your way here now, unless you entered the "/secret" path into your address bar manually.')
        return render_template('secret.html')

@app.route('/logout')
def logout():
    '''Clear current user from session and go back to root.'''

    session.pop('current_user')

    return redirect('/')

@app.route('/users/<username>')
def user_page(username):
    '''Page of user info, shown after login.'''
    
    if 'current_user' not in session:
        flash('You must be logged in to view this page!')
        return redirect('/')

    else:
        user = User.query.get_or_404(username)
        return render_template('user_page.html', user=user)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    '''Delete user from database, then redirect to "/logout".'''

    if 'current_user' not in session:
        flash('You must be logged in to view this page!')
        return redirect('/')
    
    elif session['current_user'] != username:
        flash("You can't delete someone else's account!")
        return redirect('/')

    else:
        user_to_delete = User.query.get_or_404(username)
        db.session.delete(user_to_delete)
        # models.py has cascade set up for User-Feedback relationship so associated feedback also deleted
        db.session.commit()
        flash('Your account and any feedback you had provided are now deleted.')
        return redirect('/logout')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def feedback_add(username):
    '''Form to add new feedback, and handle adding.'''

    if 'current_user' not in session:
        flash('You must be logged in to view this page!')
        return redirect('/')
    
    elif session['current_user'] != username:
        flash("You can't add feedback in someone else's account!")
        return redirect('/')

    else:
        form = AddFeedbackForm()

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            new_fdbk = Feedback(title=title, content=content, username=username)

            db.session.add(new_fdbk)
            db.session.commit()

            flash(f'Feedback (id: {new_fdbk.id}) added!')
            return redirect(f'/users/{session["current_user"]}')

        else:
            return render_template('feedback_add.html', form=form)

@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def feedback_update(feedback_id):
    '''Form to edit feedback, and handle updating.'''

    fdbk = Feedback.query.get_or_404(feedback_id)

    if 'current_user' not in session:
        flash('You must be logged in to view this page!')
        return redirect('/')
    
    elif session['current_user'] != fdbk.username:
        flash("You can't edit someone else's feedback!")
        return redirect('/')

    else:
        form = UpdateFeedbackForm(obj=fdbk)

        if form.validate_on_submit():
            fdbk.title = form.title.data
            fdbk.content = form.content.data

            db.session.commit()

            flash(f'Feedback (id: {fdbk.id}) updated!')
            return redirect(f'/users/{session["current_user"]}')

        else:
            return render_template('feedback_update.html', form=form)

@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def feedback_delete(feedback_id):
    '''Delete a specific piece of feedback.'''

    if 'current_user' not in session:
        flash('You must be logged in to view this page!')
        return redirect('/')
    
    elif session['current_user'] != fdbk.username:
        flash("You can't delete someone else's feedback!")
        return redirect('/')

    else:
        fdbk_to_delete = Feedback.query.get_or_404(feedback_id)
        db.session.delete(fdbk_to_delete)
        db.session.commit()
        flash(f'Feedback (id: {fdbk_to_delete.id}) deleted.')
        return redirect(f'/users/{session["current_user"]}')