from datetime import datetime
import json

from app import app, db, login_manager, socketio
from sqlalchemy import or_, and_
from flask import abort, flash, g, redirect, render_template, request, url_for, Markup, jsonify, session
from flask.ext.login import current_user, login_required, login_user, logout_user
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from autolink import linkify


from app.forms import LoginValidator, PostForm, MessageForm
from models import Post, User, Message

socketio = SocketIO(app)

login_manager.login_view = 'login'

async_mode = None
thread = None


@app.route('/check_messages')
@login_required
def notify_messages():
        messages = len(Message.query.filter(Message.recipient==g.user.handle).filter(Message.read==False).all()) or ""
        data = { "messages": messages }
	return jsonify(data)

@app.route('/display_messages/<cid>')
@login_required
def show_messages(cid):
	messages = len(Message.query.filter(Message.cid==cid).order_by('pub_date asc').filter(Message.read==False).all())
	data = { "messages": messages }
        return jsonify(data)


@app.route('/')
@login_required
def home():
    post = Post.query.order_by('pub_date desc').all()

    users = len(User.query.all())
    latest_post = Post.query.order_by('id desc').first()
    g.user.last_post = latest_post.id
    db.session.commit()

    user_post_count = len(Post.query.filter_by(author=g.user).all())
    new_message = len(Message.query.filter(Message.recipient==g.user.handle).filter(Message.read==False).all()) or ""
    new_post = len(Post.query.filter(Post.id>g.user.last_post).all()) or ""

    return render_template("home.html", post=post, post_count=user_post_count, users=users, new_message=new_message, new_post=new_post, async_mode=socketio.async_mode)


@app.route('/profile/<handle>')
@login_required
def profile(handle):
    user = User.query.filter_by(handle=handle).first()
    print("@" + user.handle)

    post = Post.query.filter(or_(Post.content.like("%@"+ user.handle + "%"), Post.author_id==user.id)).order_by('pub_date desc').all()
    new_post = len(Post.query.filter(Post.id>g.user.last_post).all()) or ""

    user_count = len(User.query.all())
    user_post_count = len(Post.query.filter_by(author=user).all())
    new_message = len(Message.query.filter(Message.recipient==g.user.handle).filter(Message.read==False).all()) or ""

    return render_template("profile.html", post=post, post_count=user_post_count, user_count=user_count, user=user, new_message=new_message, new_post=new_post)

@app.template_filter()
def timesince(dt, default="Just now"):
    now = datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return "Just now"

@app.route('/home/post', methods=['POST'])
@login_required
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

    return redirect(url_for('home'))


def mark_read(messages, message_cid):
    for message in messages:
	    if message.recipient == g.user.handle:
                message.read = True
            db.session.commit()


@app.route('/get_cid')
def get_cid():
    users = User.query.all()
    cids = {}
    for user in users:
        message_cid_list = sorted([str(g.user.id), str(user.id)])
        message_cid_list.insert(1, 'm')
        cids.update({user.id: ''.join(message_cid_list)})
    print(cids)
    return jsonify(cids)


@app.route('/messages')
@app.route('/messages/<recipient>')
@login_required
def messages(recipient=None):
    if recipient is None:
        lastmessage = Message.query.filter(Message.recipient==g.user.handle).order_by('pub_date desc').first()
        if lastmessage is not None:
        	recipient = lastmessage.author
    recipient_search = User.query.filter(User.handle == recipient).first()
    if recipient_search is not None:
        message_cid_list = sorted([str(g.user.id), str(recipient_search.id)])
        message_cid_list.insert(1, 'm')
        message_cid = ''.join(message_cid_list)

        messages = Message.query.filter(Message.cid==message_cid).order_by('pub_date asc').all()
        read_message = mark_read(messages, message_cid)

    else:
        messages = []
    users = len(User.query.all())
    user = User.query.filter(User.handle != g.user.handle).order_by('last_name asc').all()
    new_message = len(Message.query.filter(Message.recipient==g.user.handle).filter(Message.read==False).all()) or ""
    new_post = len(Post.query.filter(Post.id > g.user.last_post).all()) or ""

    return render_template("messages.html", user=user, recipient=recipient, messages=messages, users=users, new_message=new_message, new_post=new_post, read_message=read_message, message_cid=message_cid)


@app.route('/messages/<recipient>/send', methods=['POST'])
@login_required
def new_message(recipient):
    form = MessageForm()
    content = form.content.data
    content = Markup(content).striptags()
    content = linkify(content)

    recipient_search = User.query.filter(User.handle == recipient).first()
    recipient_id = recipient_search.id
    message_cid_list = sorted([str(g.user.id), str(recipient_id)])
    message_cid_list.insert(1, 'm')
    message_cid = ''.join(message_cid_list)

    if len(content) > 0:
        message = Message(content=content)
        message.id = len(Message.query.all())+1
        message.cid = message_cid
        message.author = g.user.handle
        message.pub_date = datetime.utcnow()
        message.recipient = recipient

        db.session.add(message)
        db.session.commit()
    else:
        flash("Messages cannot be blank.", "danger")

    return redirect(url_for('messages', recipient=recipient))


@app.route('/members')
@login_required
def members():
    users = User.query.order_by('last_name asc').all()
    user_count = len(User.query.all())
    user_post_count = len(Post.query.filter_by(author=g.user).all())

    new_message = len(Message.query.filter(Message.recipient == g.user.handle).filter(Message.read==False).all()) or ""
    new_post = len(Post.query.filter(Post.id > g.user.last_post).all()) or ""

    return render_template("members.html", post_count=user_post_count, all_users=users, user_count=user_count, user=users, new_message=new_message, new_post=new_post)


@app.route('/photos')
@login_required
def pictures():
    user_count = len(User.query.all())
    new_message = len(Message.query.filter(Message.recipient==g.user.handle).filter(Message.read==False).all()) or ""
    new_post = len(Post.query.filter(Post.id > g.user.last_post).all()) or ""

    return render_template('pictures.html', user_count=user_count, new_message=new_message, new_post=new_post)


@app.route('/calendar')
@login_required
def calendar():
    user_count = len(User.query.all())
    new_message = len(Message.query.filter(Message.recipient==g.user.handle).filter(Message.read==False).all()) or ""
    new_post = len(Post.query.filter(Post.id > g.user.last_post).all()) or ""

    return render_template('calendar.html', user_count=user_count, new_message=new_message, new_post=new_post)


@app.route('/login', methods=["GET", "POST"])
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


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


def is_logged_in():
    if g.user is not None and g.user.is_authenticated():
        return True
    return None


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user

# SOCKET CONFIGURATION - WIP


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        print("background thread function")
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)
