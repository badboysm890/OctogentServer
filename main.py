from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
import jwt
import time
import logging
import sys
from functools import wraps

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('socketio')
logger.setLevel(logging.INFO)

# Initialize Flask app and Socket.IO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your own secret key

# Configure CORS to allow connections from localhost:5500
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5500")

# In-memory data structures (consider replacing with a database in production)
users = {}
admins = {}

JWT_SECRET = 'your_jwt_secret'
JWT_ALGORITHM = 'HS256'

# Authentication decorator
def authenticate(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            logger.warning("No token provided")
            disconnect()
            return
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user = payload
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            disconnect()
            return
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            disconnect()
            return
    return wrapped

@socketio.on('connect')
@authenticate
def handle_connect():
    user = request.user
    user_id = user.get('user_id')
    company_id = user.get('company_id')
    role = user.get('role')
    sid = request.sid
    room = f"company_{company_id}"

    if not all([user_id, company_id, role]):
        logger.error("Invalid token payload")
        disconnect()
        return

    # Join the company-specific room
    join_room(room)

    if role == 'user':
        users[user_id] = {'company_id': company_id, 'sid': sid}
        # Notify admins of this company that a user connected
        for admin_id, admin_info in admins.items():
            if admin_info['company_id'] == company_id:
                socketio.emit('user_connected', {'user_id': user_id}, room=admin_info['sid'])
    elif role == 'admin':
        admins[user_id] = {'company_id': company_id, 'sid': sid}
        # Send the list of connected users to the admin
        company_users = [uid for uid, uinfo in users.items() if uinfo['company_id'] == company_id]
        socketio.emit('user_list', {'users': company_users}, room=sid)
    else:
        logger.error(f"Invalid role: {role}")
        disconnect()
        return

    logger.info(f"{role.capitalize()} '{user_id}' connected to company '{company_id}'")

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    # Find the user or admin by sid
    for user_id, info in list(users.items()):
        if info['sid'] == sid:
            company_id = info['company_id']
            del users[user_id]
            # Notify admins of this company that a user disconnected
            for admin_id, admin_info in admins.items():
                if admin_info['company_id'] == company_id:
                    socketio.emit('user_disconnected', {'user_id': user_id}, room=admin_info['sid'])
            logger.info(f"User '{user_id}' disconnected from company '{company_id}'")
            break
    else:
        for admin_id, info in list(admins.items()):
            if info['sid'] == sid:
                company_id = info['company_id']
                del admins[admin_id]
                logger.info(f"Admin '{admin_id}' disconnected from company '{company_id}'")
                break

@socketio.on('message')
@authenticate
def handle_message(data):
    user = request.user
    user_id = user.get('user_id')
    company_id = user.get('company_id')
    role = user.get('role')

    to_role = data.get('to')
    content = data.get('content')
    to_user_id = data.get('user_id')

    if not content:
        logger.warning("Empty message content")
        return

    timestamp = int(time.time())

    message = {
        'from': user_id,
        'content': content,
        'timestamp': timestamp,
    }

    if to_role == 'admin' and role == 'user':
        # Send to all admins in the company
        sent = False
        for admin_id, admin_info in admins.items():
            if admin_info['company_id'] == company_id:
                socketio.emit('message', message, room=admin_info['sid'])
                sent = True
        if not sent:
            logger.warning(f"No admins available in company '{company_id}' to receive the message")
    elif to_role == 'user' and role == 'admin':
        # Send to a specific user
        if to_user_id in users and users[to_user_id]['company_id'] == company_id:
            socketio.emit('message', message, room=users[to_user_id]['sid'])
        else:
            logger.warning(f"User '{to_user_id}' not found in company '{company_id}'")
    else:
        logger.warning(f"Unauthorized message from '{user_id}' to '{to_role}'")
        return

    logger.info(f"Message from '{user_id}' to '{to_role}'{(' ('+to_user_id+')') if to_user_id else ''}: {content}")

# Error handlers
@socketio.on_error_default
def default_error_handler(e):
    logger.error(f"An error occurred: {e}")
    disconnect()

# No need to serve static files
@app.route('/')
def index():
    return "Socket.IO Server is running."

if __name__ == '__main__':
    # Use eventlet for production-grade async workers
    import eventlet
    import eventlet.wsgi
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    socketio.run(app, host='0.0.0.0', port=8080, log_output=True)
