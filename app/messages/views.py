from flask import Blueprint, render_template, g, Markup, redirect, url_for, \
    flash
from flask_login import current_user, login_required, login_user, \
    logout_user
from autolink import linkify
from datetime import datetime

from app import app, db
from app.messages import messages as mod
from app.models import User, Message, Post
from app.forms import MessageForm


@mod.before_request
def before_request():
    g.user = current_user


@mod.route('/check_messages')
@login_required
def notify_messages():
    messages = len(Message.query.filter(Message.recipient == g.user.handle)
                   .filter(Message.read is False).all()) or ""
    data = {"messages": messages}
    return jsonify(data)


@mod.route('/display_messages/<cid>')
@login_required
def show_messages(cid):
    messages = len(Message.query.filter(Message.cid == cid)
                   .order_by('pub_date asc').filter(Message.read is False)
                   .all())
    data = {"messages": messages}
    return jsonify(data)


def mark_read(messages, message_cid):
    for message in messages:
        if message.recipient == g.user.handle:
            message.read = True
            db.session.commit()


@mod.route('/get_cid')
def get_cid():
    users = User.query.all()
    cids = {}
    for user in users:
        message_cid_list = sorted([str(g.user.id), str(user.id)])
        message_cid_list.insert(1, 'm')
        cids.update({user.id: ''.join(message_cid_list)})
    print(cids)
    return jsonify(cids)


@mod.route('/messages')
@mod.route('/messages/<recipient>')
@login_required
def messages(recipient=None):
    if recipient is None:
        lastmessage = Message.query.filter(Message.recipient ==
                                           g.user.handle).order_by(
                                               'pub_date desc').first()

        if lastmessage is not None:
            return redirect(url_for('messages.messages',
                                    recipient=lastmessage.author))
            # recipient = lastmessage.author
    recipient_search = User.query.filter(User.handle == recipient).first()

    if recipient_search is not None:
        message_cid_list = sorted([str(g.user.id), str(recipient_search.id)])
        message_cid_list.insert(1, 'm')
        message_cid = ''.join(message_cid_list)

        messages = Message.query.filter(Message.cid ==
                                        message_cid).order_by(
                                            'pub_date asc').all()
        read_message = mark_read(messages, message_cid)

    else:
        messages = []
    users = len(User.query.all())
    user = User.query.filter(User.handle !=
                             g.user.handle).order_by('last_name asc').all()

    new_message = len(Message.query.filter(Message.recipient == g.user.handle)
                      .filter(Message.read is False).all()) or ""

    new_post = len(Post.query.filter(Post.id > g.user.last_post).all()) or ""

    return render_template("messages.html", user=user, recipient=recipient,
                           messages=messages, users=users,
                           new_message=new_message, new_post=new_post,
                           read_message=read_message, message_cid=message_cid)


# @mod.route('/messages/<recipient>/send', methods=['POST'])
# @login_required
# def new_message(recipient):
    # form = MessageForm()
    # content = form.content.data
    # content = Markup(content).striptags()
    # content = linkify(content)
    #
    # recipient_search = User.query.filter(User.handle == recipient).first()
    # recipient_id = recipient_search.id
    # message_cid_list = sorted([str(g.user.id), str(recipient_id)])
    # message_cid_list.insert(1, 'm')
    # message_cid = ''.join(message_cid_list)
    #
    # if len(content) > 0:
    #     message = Message(content=content)
    #     message.id = len(Message.query.all())+1
    #     message.cid = message_cid
    #     message.author = g.user.handle
    #     message.pub_date = datetime.utcnow()
    #     message.recipient = recipient
    #
    #     db.session.add(message)
    #     db.session.commit()

    # else:
    #     flash("Messages cannot be blank.", "danger")

    # return ('', 204)
# return redirect(url_for('messages.messages', recipient=recipient))
