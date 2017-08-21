from flask import Blueprint, render_template, g
from flask_login import current_user, login_required, login_user, \
    logout_user
import glob
import os

from app import app
from app.pictures import pictures
from app.models import User, Message, Post


@pictures.before_request
def before_request():
    g.user = current_user


# @pictures.route('/photos')
# @login_required
# def pictures():
#     user_count = len(User.query.all())
#     new_message = len(Message.query.filter(Message.recipient == g.user.handle).filter(Message.read is False).all()) or ""
#     new_post = len(Post.query.filter(Post.id > g.user.last_post).all()) or ""
#
#     return render_template('pictures.html', user_count=user_count,
#                            new_message=new_message, new_post=new_post)

@pictures.route('/photos')
@pictures.route('/photos/<user>')
@login_required
def pictures(user=None):
    os.chdir(app.root_path)
    if user is None:

        photo_array = glob.glob("static/images/users/" +
                                g.user.handle + "/photos/*")
        print('photos', photo_array)
        print(app.root_path, os.getcwd())
        print("static/images/users/" + g.user.handle + "/photos/*")

    else:
        photo_array = glob.glob("static/images/users/" + user + "/photos/*")
        print('photos', photo_array)
        print(app.root_path, os.getcwd())
        print("static/images/users/" + user + "/photos/*")

    user_count = len(User.query.all())
    new_message = len(Message.query.filter
                      (Message.recipient == g.user.handle).filter
                      (Message.read is False).all()) or ""
    new_post = len(Post.query.filter(Post.id > g.user.last_post)
                   .all()) or ""

    return render_template('pictures.html', user_count=user_count,
                           new_message=new_message, new_post=new_post,
                           photo_array=photo_array)
