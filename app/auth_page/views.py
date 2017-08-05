from flask import Blueprint, render_template, redirect, request, url_for, g
from flask.ext.login import current_user, login_required, login_user, \
    logout_user

from app.auth_page import auth_page as mod
from app.forms import LoginValidator
from app.models import User
from app import login_manager


@mod.before_request
def before_request():
    g.user = current_user


def load_user(user_id):
    """
    This will be used many times like on using current_user
    :param user_id: username
    :return: user or none
    """
    agent = None
    try:
        agent = Agent.objects.get(username=user_id)
    except:
        # https://flask-login.readthedocs.org/en/latest/#how-it-works
        pass
    return agent


@mod.route('/login', methods=["GET", "POST"])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home.home'))

    if request.method == 'POST':
        login = LoginValidator(username=request.form.get('email'),
                               password=request.form.get('password'))

        if login.is_valid:
            login_user(login.lookup_user, remember=True)
            # flash('You have logged in successfully.', 'success')
            return redirect(url_for('home.home'))
        else:
            flash('Incorrect email/password', 'danger')

    return render_template('login.html')


@mod.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth_page.login'))


def is_logged_in():
    if g.user is not None and g.user.is_authenticated():
        return True
    return None


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
