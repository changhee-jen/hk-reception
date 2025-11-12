# HK Reception

Flask로 구현된 간단한 HK Reception 데모입니다. 로그인, 회원가입, 메인 대시보드를 하나의 프론트엔드 페이지에서 `fetch` 요청으로 처리합니다.

## 요구 사항 설치

```bash
pip install -r requirements.txt
```

## 데이터베이스 설정

애플리케이션은 MySQL `hk_reception` 데이터베이스의 `login` 테이블과 연동됩니다. 아래 예시는 기본 스키마와 샘플 데이터를 생성하는 SQL입니다.

```sql
CREATE DATABASE IF NOT EXISTS hk_reception;
USE hk_reception;

CREATE TABLE IF NOT EXISTS login (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO login (username, email, password, role)
VALUES
    ('admin01', 'admin@example.com', '1234', 'admin'),
    ('user01', 'user@example.com', 'abcd', 'user')
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
    password = VALUES(password),
    role = VALUES(role);
```

> ⚠️ 비밀번호는 예제의 단순화를 위해 평문으로 저장되어 있습니다. 실제 서비스에서는 반드시 해시 처리를 적용하세요.

### 환경 변수

Flask 서버가 MySQL에 접속할 수 있도록 다음 환경 변수를 설정하세요. 괄호 안은 기본값입니다.

```bash
export MYSQL_HOST=localhost        # (localhost)
export MYSQL_PORT=3306             # (3306)
export MYSQL_USER=root             # (root)
export MYSQL_PASSWORD=비밀번호     # ('')
export MYSQL_DB=hk_reception       # (hk_reception)
```

`SECRET_KEY` 환경 변수를 지정하면 Flask 세션 서명을 커스터마이즈할 수 있습니다.

## 실행 방법

```bash
python run.py
```

서버가 실행되면 브라우저에서 [http://localhost:5000](http://localhost:5000) 으로 접속하세요. 초기 화면에서 로그인/회원가입 폼이 표시되고, 제출 시 `fetch`를 통해 Flask API(`/api/*`)와 통신합니다.

## 제공되는 API 엔드포인트

| 메서드 | 경로            | 설명 |
| ------ | --------------- | ---- |
| GET    | `/api/session`  | 현재 로그인 여부와 사용자 정보를 확인합니다. |
| POST   | `/api/login`    | 아이디와 비밀번호로 로그인합니다. |
| POST   | `/api/register` | 아이디·이메일·비밀번호로 새로운 사용자를 등록합니다. |
| POST   | `/api/logout`   | 현재 세션을 로그아웃합니다. |
| GET    | `/api/home`     | 메인 화면 정보(사용자 환영 문구, 대시보드 카드)를 반환합니다. |

로그인에 성공하면 메인 화면과 대시보드 카드가 표시됩니다. 로그아웃 버튼을 누르거나 세션이 만료되면 다시 로그인 화면으로 돌아갑니다.
