from flask import Blueprint, render_template, g
from flask_login import current_user, login_required, login_user, \
    logout_user

from app import app
from app.members import members
from app.models import User, Message, Post


@members.route('/members')
@login_required
def members():
    users = User.query.order_by('last_name asc').all()
    user_count = len(User.query.all())
    user_post_count = len(Post.query.filter_by(author=g.user).all())

    new_message = len(Message.query.filter(Message.recipient == g.user.handle)
                      .filter(Message.read is False).all()) or ""
    new_post = len(Post.query.filter(Post.id > g.user.last_post).all()) or ""

    return render_template("members.html", post_count=user_post_count,
                           all_users=users, user_count=user_count, user=users,
                           new_message=new_message, new_post=new_post)
