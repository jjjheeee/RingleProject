# RingleProject

## Skills Used  
- Python 3.12.4
- Django REST Framework (DRF)
- SQLite  
- Git Bash  

---

## 실행 방법 (How to Run)

1. **Python 설치 필요**  
   [공식 사이트](https://www.python.org/downloads/)에서 Python을 설치합니다.

2. **Git Bash를 열고 가상환경 접속**

   - **Windows**
     ```bash
     source venv/Scripts/activate
     ```

   - **macOS / Linux**
     ```bash
     source venv/bin/activate
     ```

3. **Django 프로젝트 디렉토리로 이동**
   ```bash
   cd project/
   ```
4. **Django 서버 실행 하기**
   ```bash
   ** ls로 해당 폴더 내에 manage.py가 있어야한다.
   python manage.py runserver
   ```
5. **swagger api test**  
   [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
6. DBeaver 사용
   - 압축폴더 내에 project 폴더 안에 db.sqlite3 파일로 SQLite 커넥션 연결
   - Test 계정 :
      - Tutor : tutor@example.com / test1234
      - Student : student@example.com / test1234
   - 필요시 새로 회원가입 가능

## 요구사항
- 튜터가 이용할 API
   - 수업 가능한 시간대 생성 & 삭제
- 학생이 이용할 API
   - 기간 & 수업 길이로 현재 수업 가능한 시간대를 조회
   - 시간대 & 수업 길이로 수업 가능한 튜터 조회
   - 시간대, 수업길이, 튜터로 새로운 수업 신청
   - 신청한 수업 조회

## 공통 API
- 회원가입
     - 유저는 tutor or student로 회원가입 가능
     - 이메일 형식 검증
     - 비밀번호 8자리 검증
     - 이미 가입된 메일검증
- 로그인, 로그아웃
     - 유저 존재 여부 검증
     - 비밀번호 검증
     - 유저 정보와 refresh, access token 발급
     - 로그아웃시 refresh tokwn black list에 저장
- 수업 가능한 시간대 조회
   - tutor일 경우
     - 해당 날짜에 duration길이의 수업을 생성할 수 있는 시간대 조회
   - student일 경우
     - 해당 날짜에 duration길이의 신청 가능한 수업 시간대 조회
     - tutor가 생성한 수업이 해당 날짜에 없을경우 빈 list return

## tutor API (permission_classes = [IsTutor])
### tutor 회원만 접근 가능
- 내가 생성한 수업 리스트 조회 (GET)
- 수업 생성(POST)
- 수업 삭제(DELETE)
## student API (permission_classes = [IsAuthenticated])
### 로그인 회원만 접근 가능 -> 필요시 student 회원만 접근 가능
- 내가 신청한 수업 리스트 조회 (GET)
- 수업 신청(POST)
- 수업 취소(DELETE)
- 시간대와 수업 길이로 신청 가능한 수업을 조회(GET) (permission_classes = [IsStudent])

## DB 설명
![2025-04-19 13;02;34](https://github.com/user-attachments/assets/e56d9435-5cef-483d-b86f-a26df8c68dc1)
### User Table (users/models.py)
- Tutor와 Student로 룰 회원 분기
- role과 email에 db_index설정
### TutorClass Table (study/models.py)
- tutor 회원이 생성한 수업의 정보 (수업 시작시간, 수업 길이, tutor 정보, status)
- django signal을 사용해 유저가 수업을 신청하면 신청한 수업의 status를 변경
- 겹치는 시간 검증 => ex) 13:00에 60분짜리 수업 생성후 13:30에는 생성 불가
- 같은 tutor가 같은 시간에 중복생성 방지
  
### StudentClass Table (study/models.py)
-  student 회원이 신청한 수업의 정보 (수업 정보, 학생 정보, 수업 신청 날짜)
- TutorClass와 OneToOneField설정 -> 수업 하나당 한명만 신청가능
- 중복 신청 방지
