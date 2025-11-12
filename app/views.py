from contextlib import closing

import mysql.connector
from flask import Blueprint, current_app, jsonify, request, session
from mysql.connector import Error


api_bp = Blueprint('api', __name__)


def is_authenticated():
    return 'username' in session


def sanitize_username(value: str) -> str:
    return value.strip() if isinstance(value, str) else ''


def get_db_connection():
    config = current_app.config
    return mysql.connector.connect(
        host=config['MYSQL_HOST'],
        port=config['MYSQL_PORT'],
        user=config['MYSQL_USER'],
        password=config['MYSQL_PASSWORD'],
        database=config['MYSQL_DB'],
    )


def fetch_user_by_username(username: str):
    with closing(get_db_connection()) as connection:
        with closing(connection.cursor(dictionary=True)) as cursor:
            cursor.execute(
                "SELECT id, username, email, password, role, created_at FROM login WHERE username = %s",
                (username,),
            )
            return cursor.fetchone()


def fetch_user_by_email(email: str):
    with closing(get_db_connection()) as connection:
        with closing(connection.cursor(dictionary=True)) as cursor:
            cursor.execute(
                "SELECT id, username, email, password, role, created_at FROM login WHERE email = %s",
                (email,),
            )
            return cursor.fetchone()


def create_user(username: str, email: str, password: str, role: str = 'user'):
    with closing(get_db_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                "INSERT INTO login (username, email, password, role) VALUES (%s, %s, %s, %s)",
                (username, email, password, role),
            )
            connection.commit()


def build_user_payload(user_row):
    if not user_row:
        return None

    display_name = user_row.get('username')
    return {
        'id': user_row.get('id'),
        'username': user_row.get('username'),
        'email': user_row.get('email'),
        'role': user_row.get('role'),
        'name': display_name,
    }


@api_bp.get('/session')
def session_status():
    if not is_authenticated():
        return jsonify({'authenticated': False})

    username = session['username']
    try:
        user_row = fetch_user_by_username(username)
    except Error:
        current_app.logger.exception('Failed to fetch user session information')
        return jsonify({'error': '데이터베이스 오류가 발생했습니다.'}), 500

    if not user_row:
        session.pop('username', None)
        return jsonify({'authenticated': False})

    return jsonify({
        'authenticated': True,
        'user': build_user_payload(user_row),
    })


@api_bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    username = sanitize_username(data.get('username', ''))
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': '아이디와 비밀번호를 모두 입력해주세요.'}), 400

    try:
        user_row = fetch_user_by_username(username)
    except Error:
        current_app.logger.exception('Login query failed')
        return jsonify({'error': '로그인 처리 중 문제가 발생했습니다.'}), 500

    if not user_row or user_row.get('password') != password:
        return jsonify({'error': '아이디 또는 비밀번호가 올바르지 않습니다.'}), 401

    session['username'] = username
    return jsonify({
        'message': '성공적으로 로그인했습니다.',
        'user': build_user_payload(user_row),
    })


@api_bp.post('/register')
def register():
    data = request.get_json(silent=True) or {}

    username = sanitize_username(data.get('username', ''))
    email = (data.get('email', '') or '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not username or not email or not password:
        return jsonify({'error': '모든 필드를 입력해주세요.'}), 400

    if password != confirm_password:
        return jsonify({'error': '비밀번호가 일치하지 않습니다.'}), 400

    try:
        if fetch_user_by_username(username):
            return jsonify({'error': '이미 존재하는 아이디입니다.'}), 409

        if fetch_user_by_email(email):
            return jsonify({'error': '이미 등록된 이메일입니다.'}), 409

        create_user(username, email, password)
    except Error:
        current_app.logger.exception('Registration failed')
        return jsonify({'error': '회원가입 처리 중 문제가 발생했습니다.'}), 500

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
    try:
        user_row = fetch_user_by_username(username)
    except Error:
        current_app.logger.exception('Failed to load home data')
        return jsonify({'error': '대시보드 정보를 불러오지 못했습니다.'}), 500

    if not user_row:
        session.pop('username', None)
        return jsonify({'authenticated': False}), 401

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
        'user': build_user_payload(user_row),
        'dashboard': dashboard_cards,
    })
