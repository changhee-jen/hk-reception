from flask import Blueprint, jsonify, request, session


api_bp = Blueprint('api', __name__)

# In-memory user store for demo purposes
USERS = {
    'guest': {
        'name': 'Guest User',
        'password': 'guest'
    }
}


def is_authenticated():
    return 'username' in session


def sanitize_username(value: str) -> str:
    return value.strip() if isinstance(value, str) else ''


@api_bp.get('/session')
def session_status():
    if not is_authenticated():
        return jsonify({'authenticated': False})

    username = session['username']
    user = USERS.get(username, {'name': username})
    return jsonify({
        'authenticated': True,
        'user': {
            'username': username,
            'name': user.get('name', username)
        }
    })


@api_bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    username = sanitize_username(data.get('username', ''))
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': '아이디와 비밀번호를 모두 입력해주세요.'}), 400

    user = USERS.get(username)
    if not user or user['password'] != password:
        return jsonify({'error': '아이디 또는 비밀번호가 올바르지 않습니다.'}), 401

    session['username'] = username
    return jsonify({
        'message': '성공적으로 로그인했습니다.',
        'user': {
            'username': username,
            'name': user.get('name', username)
        }
    })


@api_bp.post('/register')
def register():
    data = request.get_json(silent=True) or {}

    username = sanitize_username(data.get('username', ''))
    name = sanitize_username(data.get('name', ''))
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not username or not name or not password:
        return jsonify({'error': '모든 필드를 입력해주세요.'}), 400

    if password != confirm_password:
        return jsonify({'error': '비밀번호가 일치하지 않습니다.'}), 400

    if username in USERS:
        return jsonify({'error': '이미 존재하는 아이디입니다.'}), 409

    USERS[username] = {
        'name': name,
        'password': password,
    }

    return jsonify({'message': '회원가입이 완료되었습니다. 로그인해주세요.'}), 201


@api_bp.post('/logout')
def logout():
    session.pop('username', None)
    return jsonify({'message': '로그아웃되었습니다.'})


@api_bp.get('/home')
def home():
    if not is_authenticated():
        return jsonify({'authenticated': False}), 401

    username = session['username']
    user = USERS.get(username, {'name': username})

    dashboard_cards = [
        {
            'title': '오늘의 방문 예정',
            'description': '예약된 방문자 3명',
            'icon': '👥',
        },
        {
            'title': '확인 대기',
            'description': '입장 승인 대기 1건',
            'icon': '⏳',
        },
        {
            'title': '공지사항',
            'description': '새로운 보안 지침을 확인하세요.',
            'icon': '📢',
        },
    ]

    return jsonify({
        'authenticated': True,
        'user': {
            'username': username,
            'name': user.get('name', username)
        },
        'dashboard': dashboard_cards,
    })
