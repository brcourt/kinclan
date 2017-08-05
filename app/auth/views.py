from flask import Blueprint, render_template
from flask.ext.login import current_user, login_required, login_user, \
    logout_user

#auth_page = Blueprint('auth_page', __name__, template_folder='templates')

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


@auth_page.route('/login', methods=["GET", "POST"])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home'))

    if request.method == 'POST':
        login = LoginValidator(username=request.form.get('email'),
                               password=request.form.get('password'))

        if login.is_valid:
            login_user(login.lookup_user, remember=True)
            # flash('You have logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Incorrect email/password', 'danger')

    return render_template('login.html')


@auth_page.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


def is_logged_in():
    if g.user is not None and g.user.is_authenticated():
        return True
    return None


# @login_manager.user_loader
# def load_user(id):
#     return User.query.get(int(id))
