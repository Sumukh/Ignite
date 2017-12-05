from flask_login import current_user

from flask_socketio import join_room, leave_room, send
from appname.extensions import socketio

@socketio.on('connect')
def connect():
    if not current_user.is_authenticated:
        pass
    return

@socketio.on('disconnect')
def disconnect():
    if not current_user.is_authenticated:
        pass
    return

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)
