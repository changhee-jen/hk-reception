# HK Reception

Flask로 구현된 간단한 HK Reception 데모입니다. 로그인, 회원가입, 메인 대시보드를 하나의 프론트엔드 페이지에서 `fetch` 요청으로 처리합니다.

## 요구 사항 설치

```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
python run.py
```

서버가 실행되면 브라우저에서 [http://localhost:5000](http://localhost:5000) 으로 접속하세요. 초기 화면에서 로그인/회원가입 폼이 표시되고, 제출 시 `fetch`를 통해 Flask API(`/api/*`)와 통신합니다.

## 제공되는 API 엔드포인트

| 메서드 | 경로            | 설명 |
| ------ | --------------- | ---- |
| GET    | `/api/session`  | 현재 로그인 여부를 확인합니다. |
| POST   | `/api/login`    | 아이디와 비밀번호로 로그인합니다. |
| POST   | `/api/register` | 새로운 사용자를 등록합니다. |
| POST   | `/api/logout`   | 현재 세션을 로그아웃합니다. |
| GET    | `/api/home`     | 메인 화면 정보(사용자 환영 문구, 대시보드 카드)를 반환합니다. |

### 기본 계정

- 아이디: `guest`
- 비밀번호: `guest`

로그인에 성공하면 메인 화면과 대시보드 카드가 표시됩니다. 로그아웃 버튼을 누르거나 세션이 만료되면 다시 로그인 화면으로 돌아갑니다.
