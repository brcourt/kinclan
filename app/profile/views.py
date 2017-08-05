from flask import Blueprint, render_template, g
from flask.ext.login import current_user, login_required, login_user, \
    logout_user
from sqlalchemy import or_, and_


from app import app
from app.profile import profile
from app.models import User, Message, Post


@app.before_request
def before_request():
    g.user = current_user


@profile.route('/profile/<handle>')
@login_required
def profile(handle):
    user = User.query.filter_by(handle=handle).first()
    print("@" + user.handle)

    post = Post.query.filter(or_(Post.content.like("%@" + user.handle + "%"), Post.author_id == user.id)).order_by('pub_date desc').all()
    new_post = len(Post.query.filter(Post.id > g.user.last_post).all()) or ""

    user_count = len(User.query.all())
    user_post_count = len(Post.query.filter_by(author=user).all())
    new_message = len(Message.query.filter(Message.recipient == g.user.handle).filter(Message.read is False).all()) or ""

    return render_template("profile.html", post=post,
                           post_count=user_post_count, user_count=user_count,
                           user=user, new_message=new_message,
                           new_post=new_post)
