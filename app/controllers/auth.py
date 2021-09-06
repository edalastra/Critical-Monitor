from app import app
from flask_login import login_user
from flask import Blueprint, render_template
from app.models.Forms import SignupForm

auth = Blueprint('user', __name__) 


@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    # form = LoginForm()
    # if form.validate_on_submit():
    #     login_user(user)

    #     flask.flash('Usuário autenticado')

    #     next = flask.request.args.get('next')
    

    #     return flask.redirect(next or flask.url_for('index'))
    return render_template('signin.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        print(form.name.data)

    return render_template('signup.html', form_signup=form )

@auth.route('/logout')
def logout():
    return 'Logout'