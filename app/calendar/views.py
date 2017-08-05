from flask import Blueprint, render_template, g
from flask.ext.login import current_user, login_required, login_user, \
    logout_user

from app import app
from app.calendar import calendar
from app.models import User, Message, Post


@app.before_request
def before_request():
    g.user = current_user


@calendar.route('/calendar')
@login_required
def calendar():
    user_count = len(User.query.all())
    new_message = len(Message.query.filter(Message.recipient == g.user.handle)
                      .filter(Message.read is False).all()) or ""
    new_post = len(Post.query.filter(Post.id > g.user.last_post).all()) or ""

    return render_template('calendar.html', user_count=user_count,
                           new_message=new_message, new_post=new_post)
