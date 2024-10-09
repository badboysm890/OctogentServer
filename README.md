# Live Chat Application with Chatbot Integration

## Overview

This application provides a real-time chat platform that integrates with your existing chatbot server. Users interacting with the chatbot can be seamlessly transferred to a live agent (admin) when needed. The application uses JWT (JSON Web Tokens) for secure authentication and communication.

## Features

- **Seamless Chatbot Integration**: Users can transition from chatbot interactions to live agents smoothly.
- **Real-time Communication**: Supports instant messaging between users and admins.
- **JWT Authentication**: Secure authentication using JWT tokens.
- **Multi-company Support**: Ensures users and admins communicate within their respective companies.
- **Extensibility**: Designed for easy integration and future enhancements.

---

## Table of Contents

- [Live Chat Application with Chatbot Integration](#live-chat-application-with-chatbot-integration)
  - [Overview](#overview)
  - [Features](#features)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Setup and Installation](#setup-and-installation)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Create a Virtual Environment (Optional but Recommended)](#2-create-a-virtual-environment-optional-but-recommended)
    - [3. Install Dependencies](#3-install-dependencies)
  - [Configuration](#configuration)
    - [1. Set Secret Keys](#1-set-secret-keys)
    - [2. Configure CORS (if needed)](#2-configure-cors-if-needed)
  - [Running the Application](#running-the-application)
  - [Generating JWT Tokens](#generating-jwt-tokens)
    - [Using jwt.io](#using-jwtio)
    - [Using a Python Script](#using-a-python-script)
  - [Client-side Implementation](#client-side-implementation)
    - [User Client JavaScript](#user-client-javascript)
    - [Admin Client JavaScript](#admin-client-javascript)
  - [Integration with Chatbot Server](#integration-with-chatbot-server)
  - [Error Handling and Debugging](#error-handling-and-debugging)
  - [Security Considerations](#security-considerations)
  - [Extending the Application](#extending-the-application)
  - [Conclusion](#conclusion)

---

## Prerequisites

- **Python 3.7 or higher**
- **pip** package manager
- **Eventlet** for asynchronous I/O
- **Flask and Flask-SocketIO** for web and WebSocket handling
- **PyJWT** for JWT token handling
- **Basic understanding of JWT and RESTful APIs**

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/badboysm890/OctogentServer.git
cd OctogentServer
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install Dependencies

Create a `requirements.txt` file with the following content:

```txt
Flask==2.1.3
Flask-SocketIO==5.2.0
PyJWT==2.4.0
eventlet==0.33.1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

### 1. Set Secret Keys

In `main.py`, replace `'your_secret_key'` and `'your_jwt_secret'` with your own secure secret keys:

```python
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your own secret key
JWT_SECRET = 'your_jwt_secret'  # Replace with your own JWT secret key
```

- **Note**: Keep these keys secure and do not expose them in version control.

### 2. Configure CORS (if needed)

In `main.py`, the Socket.IO server allows all origins by default (`cors_allowed_origins="*"`). If you want to restrict access to specific domains, modify this setting:

```python
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5500"])  # Adjust as needed
```

---

## Running the Application

Start the server:

```bash
python main.py
```

- The server will run on `http://localhost:8080` by default.

---

## Generating JWT Tokens

### Using jwt.io

You can generate JWT tokens manually using [jwt.io](https://jwt.io/):

1. **Go to** [jwt.io](https://jwt.io/).

2. **In the "Decoder" section**, under **PAYLOAD**, enter:

   ```json
   {
     "company_id": "YourCompanyID",
     "user_id": "UserID",
     "role": "user",  // or "admin"
     "exp": <Expiration Time as Unix Timestamp>
   }
   ```

   - Replace `YourCompanyID` with your company identifier.
   - Replace `UserID` with the user's unique identifier.
   - Set `role` to `"user"` or `"admin"`.
   - Set `exp` to the expiration time (current Unix timestamp plus desired validity period).

3. **In the "VERIFY SIGNATURE" section**:

   - Set the algorithm to `HS256`.
   - Enter your `JWT_SECRET` as the secret key.

4. **Copy the token** from the "Encoded" section on the left. This is your JWT token.

### Using a Python Script

Alternatively, you can use a Python script to generate tokens.

Create a file named `generate_token.py`:

```python
import jwt
import time

JWT_SECRET = 'your_jwt_secret'  # Must match with JWT_SECRET in main.py
JWT_ALGORITHM = 'HS256'

def generate_token(company_id, user_id, role, expiration_seconds=3600):
    payload = {
        'company_id': company_id,
        'user_id': user_id,
        'role': role,
        'exp': int(time.time()) + expiration_seconds
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

if __name__ == '__main__':
    company_id = input('Enter Company ID: ')
    user_id = input('Enter User ID: ')
    role = input('Enter Role (user/admin): ')
    token = generate_token(company_id, user_id, role)
    print(f'\\nGenerated JWT Token:\\n{token}\\n')
```

Run the script:

```bash
python generate_token.py
```

Follow the prompts to enter `company_id`, `user_id`, and `role`. The script will output the generated JWT token.

---

## Client-side Implementation

### User Client JavaScript

Below is the JavaScript snippet for the user client (`user.html`):

```html
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
    var socket;

    function connect() {
        var token = document.getElementById('token').value.trim();
        if (!token) {
            alert('Please enter a JWT token.');
            return;
        }

        socket = io('http://localhost:8080', { query: { token: token } });

        socket.on('connect', function() {
            document.getElementById('status').innerHTML = 'Connected';
            document.getElementById('login').style.display = 'none';
            document.getElementById('chat').style.display = 'block';
        });

        socket.on('disconnect', function() {
            document.getElementById('status').innerHTML = 'Disconnected';
            document.getElementById('login').style.display = 'block';
            document.getElementById('chat').style.display = 'none';
        });

        socket.on('message', function(data) {
            var messages = document.getElementById('messages');
            var timestamp = new Date(data.timestamp * 1000).toLocaleTimeString();
            messages.innerHTML += '<p><strong>' + data.from + ' (' + timestamp + '):</strong> ' + data.content + '</p>';
            messages.scrollTop = messages.scrollHeight;
        });

        socket.on('chatbot_context', function(data) {
            var messages = document.getElementById('messages');
            messages.innerHTML += '<p><em>Chatbot context:</em> ' + data.context + '</p>';
        });

        socket.on('connect_error', function(error) {
            alert('Connection Error: ' + error.message);
        });
    }

    function sendMessage() {
        var message = document.getElementById('messageInput').value.trim();
        if (message === '') {
            alert('Please enter a message.');
            return;
        }
        socket.emit('message', { to: 'admin', content: message });
        document.getElementById('messageInput').value = '';
    }
</script>
```

### Admin Client JavaScript

Below is the JavaScript snippet for the admin client (`admin.html`):

```html
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
    var socket;
    var users = [];

    function connect() {
        var token = document.getElementById('token').value.trim();
        if (!token) {
            alert('Please enter a JWT token.');
            return;
        }

        socket = io('http://localhost:8080', { query: { token: token } });

        socket.on('connect', function() {
            document.getElementById('status').innerHTML = 'Connected';
            document.getElementById('login').style.display = 'none';
            document.getElementById('chat').style.display = 'block';
        });

        socket.on('disconnect', function() {
            document.getElementById('status').innerHTML = 'Disconnected';
            document.getElementById('login').style.display = 'block';
            document.getElementById('chat').style.display = 'none';
        });

        socket.on('user_list', function(data) {
            users = data.users;
            updateUserList();
        });

        socket.on('user_connected', function(data) {
            users.push(data.user_id);
            updateUserList();
        });

        function updateUserList() {
            var userList = document.getElement

ById('userList');
            userList.innerHTML = '';
            users.forEach(function(user) {
                userList.innerHTML += '<p>User: ' + user + '</p>';
            });
        }

        socket.on('user_disconnected', function(data) {
            users = users.filter(function(user) {
                return user !== data.user_id;
            });
            updateUserList();
        });

        socket.on('message', function(data) {
            var messages = document.getElementById('messages');
            var timestamp = new Date(data.timestamp * 1000).toLocaleTimeString();
            messages.innerHTML += '<p><strong>' + data.from + ' (' + timestamp + '):</strong> ' + data.content + '</p>';
            messages.scrollTop = messages.scrollHeight;
        });

        socket.on('connect_error', function(error) {
            alert('Connection Error: ' + error.message);
        });
    }

    function sendMessage() {
        var message = document.getElementById('messageInput').value.trim();
        var userId = document.getElementById('userId').value.trim();
        if (message === '' || userId === '') {
            alert('Please enter both user ID and message.');
            return;
        }
        socket.emit('message', { to: 'user', user_id: userId, content: message });
        document.getElementById('messageInput').value = '';
    }
</script>
```

---

## Integration with Chatbot Server

The chatbot server should call the `/transfer_to_agent` endpoint whenever the bot determines that the user needs to be transferred to a live agent. The chatbot must send the `user_id`, `company_id`, and optional `context` (chat history or other relevant details).

Example request:

```json
{
  "user_id": "user123",
  "company_id": "companyA",
  "context": "User is unsatisfied with the bot response..."
}
```

---

## Error Handling and Debugging

- **Token Expiration**: JWT tokens are checked for expiration. Users and admins will be disconnected if their token is invalid.
- **Connection Errors**: Frontend clients will receive `connect_error` events if they fail to authenticate or connect to the server.
- **Unhandled Errors**: The server logs all unhandled exceptions and disconnects the client if an error occurs.

---

## Security Considerations

- Use secure JWT tokens with appropriate expiration times.
- Always validate the token before granting access.
- Restrict CORS in production environments.

---

## Extending the Application

- **Multi-room support**: You can add more granularity by allowing multiple rooms within the same company.
- **Database Integration**: For production use, replace in-memory structures with persistent storage solutions.
- **Logging**: Add more detailed logging for auditing and monitoring.

---

## Conclusion

This chat application allows seamless integration between chatbot and live agents, providing a robust communication platform for multiple companies and users.
