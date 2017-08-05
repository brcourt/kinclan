from flask import Blueprint, render_template, g, Markup, redirect, url_for
from flask.ext.login import current_user, login_required, login_user, \
    logout_user
from flask.ext.sqlalchemy import SQLAlchemy
from autolink import linkify
from datetime import datetime

from app import db
from app.forms import PostForm
from app.utils import timesince
from app.models import Post, User, Message
from app.home import home as mod


@mod.before_request
def before_request():
    g.user = current_user


@mod.route('/')
# @login_required
def home():
    post = Post.query.order_by('pub_date desc').all()

    users = len(User.query.all())
    latest_post = Post.query.order_by('id desc').first()
    g.user.last_post = latest_post.id
    db.session.commit()

    user_post_count = len(Post.query.filter_by(author=g.user).all())
    new_message = len(Message.query.filter(Message.recipient == g.user.handle)
                      .filter(Message.read is False).all()) or ""
    new_post = len(Post.query.filter(Post.id > g.user.last_post).all()) or ""
    return render_template("home.html", post=post, post_count=user_post_count,
                           users=users, new_message=new_message,
                           new_post=new_post)


@mod.route('/home/post', methods=['POST'])
# @login_required
def new_post():
    form = PostForm()
    content = form.content.data
    content = Markup(content).striptags()
    content = linkify(content)

    if len(content) > 0:
        post = Post(content=content)
        post.author = g.user
        post.pub_date = datetime.utcnow()
        post.read = True

        db.session.add(post)
        db.session.commit()
    else:
        flash("Status updates cannot be blank.", "warning")

    return redirect(url_for('home.home'))
