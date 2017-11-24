from flask import session, g, request, Markup
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, \
    rooms, disconnect
from autolink import linkify
from flask_login import current_user
from datetime import datetime


from app import socketio, db
from app.chat import chat
from app.forms import MessageForm
from app.models import User, Message


@chat.before_request
def before_request():
    g.user = current_user


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})
    print("my_event triggered")


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)
    print("broadcast triggered")


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
def send_room_message(author, recipient, message):
    print('message: ', message)
    print('author: ', author[0], author[1])
    print('recipient: ', recipient)

    form = MessageForm()
    content = message['data']
    content = Markup(content).striptags()
    content = linkify(content)

    if message['data'] != "":
        emit('room_message', {'data': message['data'], 'author': author,
                              'recipient': recipient}, room=message['room'])

    if message['room'] == author[0]:
        pass

    else:
        recipient_search = User.query.filter(User.handle == recipient).first()
        recipient_id = recipient_search.id
        message_cid_list = sorted([str(author[1]), str(recipient_id)])
        message_cid_list.insert(1, 'm')
        message_cid = ''.join(message_cid_list)

        if len(content) > 0:
            message = Message(content=content)
            message.id = len(Message.query.all())+1
            message.cid = message_cid
            message.author = author[0]
            message.pub_date = datetime.utcnow()
            message.recipient = recipient

            db.session.add(message)
            db.session.commit()


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)
