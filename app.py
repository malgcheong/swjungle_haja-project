from bson import ObjectId
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import datetime, certifi
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
SECRET_KEY = 'your_secret_key123123'

app = Flask(__name__)

# MongoDB 연결
ca = certifi.where()
client = MongoClient('mongodb+srv://skacjddn:1234@cluster0.do59mm5.mongodb.net/?retryWrites=true&w=majority', tlsCAFile = ca)
db = client.db_jungle# 여기에 본인의 MongoDB 데이터베이스 이름을 넣으세요


# 시작 페이지
@app.route('/')
def index_page():
    return render_template('index.html')


# 로그인
@app.route('/login', methods=['POST'])
def login():
    # 클라이언트에서 제출한 사용자 이름과 비밀번호 가져오기
    user_email = request.json.get('email')
    password = request.json.get('password')


    # MongoDB에서 사용자 정보 조회
    user = db.users.find_one({'email': user_email})

    if user and check_password_hash(user['password'], password):  # 비밀번호 해싱 체크

        payload = {
            'user_name': user['user_name'],
            'email': user['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'token': token, 'user': user['user_name'], 'email': user['email']}), 200

    # 인증 실패시 에러 반환
    return jsonify({'error': 'Invalid username or password'}), 401


# 회원 가입
@app.route('/api/sign_up', methods=['GET', 'POST'])
def sign_up():
    # 회원 가입 요청일 때
    if request.method == 'POST':
        # 사용자 정보 가져오기
        user_email = request.form['email']
        user_name = request.form['username']
        password = generate_password_hash(request.form['password'])

        # 이메일 중복 확인 후 사용자 정보 MongoDB에 저장
        user = db.users.find_one({'email': user_email})
        if user:
            return jsonify({'message': 'User already exists', 'user_name': user['user_name']}), 409
        else:
            db.users.insert_one({'user_name': user_name, 'email': user_email, 'password': password})

        # 회원가입 성공시 메시지 반환
        return jsonify({'message': 'User registered successfully', 'user_name': user_name})

    return render_template('sign_up.html')


# 메인 haja 페이지 이동
@app.route('/api/board/main', methods=['GET'])
def board_main():
    # Extract JWT token from the request cookie
    jwt_token = request.cookies.get('token')

    if not jwt_token:
        # If JWT token is not present in the cookie, return an error response
        return jsonify({'error': 'JWT token is missing'}), 401

    try:
        jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])

        # 모든 게시글 가져오기
        all_results = list(db.board.find({}))

        # 진행상태는 아직 안정해졌고, 모집상태가 on인것만 반환
        filtered_results = []
        for item in all_results:
            if item.get('status') == '' and item.get('meet') == 'on':
                item['_id'] = str(item['_id'])
                filtered_results.append(item)
        filtered_results.reverse()
        return render_template('main_haja.html', result=filtered_results)

    except jwt.ExpiredSignatureError:
        # Handle expired token
        return jsonify({'error': 'JWT token has expired'}), 401

    except jwt.InvalidTokenError:
        # Handle invalid token (e.g., tampered token)
        return jsonify({'error': 'Invalid JWT token'}), 401

    except Exception as e:
        # Handle other exceptions
        return jsonify({'error': str(e)}), 401


# 내가 만든 haja 페이지 이동
@app.route('/api/board/my', methods=['GET'])
def board_my():
    # Extract JWT token from the request cookie
    jwt_token = request.cookies.get('token')

    if not jwt_token:
        # If JWT token is not present in the cookie, return an error response
        return jsonify({'error': 'JWT token is missing'}), 401

    try:
        token=jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
        user_name = token.get('user_name')
        # 모든 게시글 가져오기
        all_results = list(db.board.find({}))

        # 진행상태는 안정해졌고(''), 모집상태가 on이고, 글쓴 host가 user_name인것만 반환
        filtered_results = []
        for item in all_results:
            for user in item.get('user'):
                if item.get('status') == '' and item.get('meet') == 'on' and user.get('user_role') == 'host' and user.get(
                        'user_name') == user_name:
                    item['_id'] = str(item['_id'])
                    filtered_results.append(item)
        filtered_results.reverse()
        return render_template('my_haja.html', result=filtered_results)
    except jwt.ExpiredSignatureError:
        # Handle expired token
        return jsonify({'error': 'JWT token has expired'}), 401

    except jwt.InvalidTokenError:
        # Handle invalid token (e.g., tampered token)
        return jsonify({'error': 'Invalid JWT token'}), 401

    except Exception as e:
        # Handle other exceptions
        return jsonify({'error': str(e)}), 401


# 진행중인 haja 페이지 이동
@app.route('/api/board/ongo', methods=['GET'])

def board_ongo():
    # Extract JWT token from the request cookie
    jwt_token = request.cookies.get('token')

    if not jwt_token:
        # If JWT token is not present in the cookie, return an error response
        return jsonify({'error': 'JWT token is missing'}), 401

    try:
        token=jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
        user_name = token.get('user_name')
    # 모든 게시글 가져오기
        all_results = list(db.board.find({}))

        # 진행상태는  ongo, 모집상태가 off인것만 반환
        filtered_results = []
        for item in all_results:
            for user in item.get('user'):
                if item.get('status') == 'ongo' and item.get('meet') == 'off' and user.get(
                        'user_name') == user_name:
                    item['_id'] = str(item['_id'])
                    filtered_results.append(item)
        filtered_results.reverse()
        return render_template('ongo_haja.html', result=filtered_results)

    except jwt.ExpiredSignatureError:
        # Handle expired token
        return jsonify({'error': 'JWT token has expired'}), 401

    except jwt.InvalidTokenError:
        # Handle invalid token (e.g., tampered token)
        return jsonify({'error': 'Invalid JWT token'}), 401

    except Exception as e:
        # Handle other exceptions
        return jsonify({'error': str(e)}), 401


# 완료된 haja 페이지 이동
@app.route('/api/board/end', methods=['GET'])

def board_end():
    # Extract JWT token from the request cookie
    jwt_token = request.cookies.get('token')

    if not jwt_token:
        # If JWT token is not present in the cookie, return an error response
        return jsonify({'error': 'JWT token is missing'}), 401

    try:
        token=jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
        user_name = token.get('user_name')
    # 모든 게시글 가져오기
        all_results = list(db.board.find({}))

        # 진행상태는 end이고, 모집상태가 off인것만 반환
        filtered_results = []
        for item in all_results:
            for user in item.get('user'):
                if item.get('status') == 'end' and item.get('meet') == 'off' and user.get(
                        'user_name') == user_name:
                    item['_id'] = str(item['_id'])
                    filtered_results.append(item)
        filtered_results.reverse()
        return render_template('end_haja.html', result=filtered_results)

    except jwt.ExpiredSignatureError:
        # Handle expired token
        return jsonify({'error': 'JWT token has expired'}), 401

    except jwt.InvalidTokenError:
        # Handle invalid token (e.g., tampered token)
        return jsonify({'error': 'Invalid JWT token'}), 401

    except Exception as e:
        # Handle other exceptions
        return jsonify({'error': str(e)}), 401


# 게시글 검색
@app.route('/api/board/search', methods=['GET'])

def search_board():
    # 시간, 장소, 내용에 해당 텍스트가 포함되는 모든 문서 검색
    search = request.args.get('search')
    if not search:
        return jsonify({'error': 'input search string!'}), 400
    # MongoDB의 $text 쿼리를 사용하여 검색 수행
    # 시간, 장소, 내용 필드에 대해 정확한 일치 검색 수행
    query = {
        '$or': [
            {'when': {'$regex': search, '$options': 'i'}},  # 시간 필드
            {'where': {'$regex': search, '$options': 'i'}},  # 장소 필드
            {'what': {'$regex': search, '$options': 'i'}}  # 내용 필드
        ]
    }

    result = db.board.find(query)

    # 검색 결과 처리
    result_list = list(result)

    # ObjectId를 문자열로 변환하여 직렬화 가능하도록 함
    for item in result_list:
        item['_id'] = str(item['_id'])

    # 검색 결과 처리
    if len(result_list) == 0:
        return jsonify({'message': 'no results'}), 500
    else:
        return jsonify(result_list), 200


# 메인 haja 페이지에서 참가 버튼 클릭시
@app.route('/api/board/main/join', methods=['POST'])

def board_main_join():
    # 참가 버튼 클릭시 update 참여 인원+1, 참가자 추가
    jwt_token = request.cookies.get('token')

    if not jwt_token:
        # If JWT token is not present in the cookie, return an error response
        return jsonify({'error': 'JWT token is missing'}), 401
    token = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
    user_name = token.get('user_name')

    user = {'user_name': user_name, 'user_role': 'guest', 'user_check': 'N'}

    # 기존 보드의 ID
    board_id = request.form.get('board_id')

    # 기존 보드를 찾음
    board = db.board.find_one({'_id': ObjectId(board_id)})
    if board:
        # 최대 참여 가능 인원이 꽉 차 있을 때
        if board['max'] == len(board['user']):
            return jsonify({'message': 'Do not more participate. It\'s Full!'}), 500

        # 똑같은 인원이 또 참여를 눌렀을 경우
        for user_item in board.get('user', []):
            if user_item.get('user_name') == user_name:
                return jsonify({'message': 'The same ID should not participate.'}), 500
        
        # 기존 보드에 유저 추가
        board['user'].append(user)
        # 업데이트된 보드를 저장
        db.board.update_one({'_id': ObjectId(board_id)}, {'$set': board})

        # return redirect(url_for('board_main'))
        return jsonify({'message': 'join success!', 'user': user})
    else:
        return jsonify({'message': 'Board not found.'}), 500


# haja 등록
@app.route('/api/board/regi', methods=['POST'])
def regi_board():

    # 사용자 정보 가져오기
    jwt_token = request.cookies.get('token')

    if not jwt_token:
        # If JWT token is not present in the cookie, return an error response
        return jsonify({'error': 'JWT token is missing'}), 401

    token = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])

    user_name = token.get('user_name')

    user_role = 'host'
    user_check = 'N'

    # 클라이언트로부터 폼 데이터 추출
    when = request.form.get('when')
    where = request.form.get('where')
    what = request.form.get('what')
    content = request.form.get('content')
    max_num = int(request.form.get('max')) if request.form.get('max') else None

    # 사용자 정보 추출
    users = []
    user = {'user_name': user_name, 'user_role': user_role, 'user_check': user_check}
    users.append(user)

    # 초기 haja 등록시 모집상태(모집 중인지)
    meet = 'on'

    # 초기 haja 등록시 진행상태(진행하고 있는지)
    status = ''
    data = {
        'own': user_name,
        'when': when,
        'where': where,
        'what': what,
        'content': content,
        'max': max_num,
        'user': users,
        'meet': meet,
        'status': status
    }
    result = db.board.insert_one(data)
    board = db.board.find_one({'_id': result.inserted_id})
    board['_id'] = str(board['_id'])

    if result.inserted_id:
        return jsonify({'message': "register board successfully!", 'board': board}), 200
    else:
        return jsonify({'message': "register board fail!"}), 500


# 내가 만든 haja 마감
@app.route('/api/board/my/close', methods=['POST'])

def close_board():
    jwt_token = request.cookies.get('token')

    if not jwt_token:
        # If JWT token is not present in the cookie, return an error response
        return jsonify({'error': 'JWT token is missing'}), 401
    board_id = request.form.get('board_id')
    db.board.update_one({'_id': ObjectId(board_id)}, {'$set': {'meet': 'off', 'status': 'ongo'}})
    return redirect(url_for('board_my'))


# 내가 만든 haja 수정
@app.route('/api/board/my/update', methods=['POST'])

def update_board():
    jwt_token = request.cookies.get('token')

    if not jwt_token:
        # If JWT token is not present in the cookie, return an error response
        return jsonify({'error': 'JWT token is missing'}), 401
    # 클라이언트로부터 폼 데이터 추출
    when = request.form.get('when')
    where = request.form.get('where')
    what = request.form.get('what')
    content = request.form.get('content')
    max_num = request.form.get('max_num')

    # 기존 보드의 ID
    board_id = request.form['board_id']

    # 기존 보드 수정
    result = db.board.update_one({'_id': ObjectId(board_id)}, {
        '$set': {'when': when, 'where': where, 'what': what, 'content': content, 'max': max_num}})

    board = db.board.find_one({'_id': ObjectId(board_id)})
    board['_id'] = str(board['_id'])

    if result.modified_count > 0:
        return jsonify({'message': "update board successfully!", 'board': board}), 200
    else:
        return jsonify({'message': "update board fail!", 'board': board}), 500


# 내가 만든 haja 삭제
@app.route('/api/board/my/delete', methods=['POST'])

def delete_board():
    jwt_token = request.cookies.get('token')

    if not jwt_token:
        # If JWT token is not present in the cookie, return an error response
        return jsonify({'error': 'JWT token is missing'}), 401

    board_id = request.form.get('board_id')

    result = db.board.delete_one({'_id': ObjectId(board_id)})

    if result.deleted_count:
        return jsonify({'message': 'delete board successfully'}), 200
    else:
        return jsonify({'message': 'can not delete board!'}), 500


# 진행중인 haja 완료
@app.route('/api/board/ongo/check', methods=['POST'])

def board_check():
    # 완료 버튼 클릭시 update 참가자 체크 & 모든 참가자가 체크 상태일 시 => 게시글의 상태를 완료 상태로 변경

    jwt_token = request.cookies.get('token')

    if not jwt_token:
        # If JWT token is not present in the cookie, return an error response
        return jsonify({'error': 'JWT token is missing'}), 401

    token = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])

    #완료하고자 하는 user
    user_name = token.get('user_name')
    # 기존 보드의 ID
    board_id = request.form.get('board_id')

    # 해당 board를 조회
    board = db.board.find_one({'_id': ObjectId(board_id)})

    onuser = []

    if board:
        # user 배열에서 user_name이 일치하는 요소를 찾음
        for user in board['user']:
            if user['user_name'] == user_name:
                # user_check 값을 변경
                user['user_check'] = 'Y'
                onuser = {'user_name': user_name, 'user_check': user['user_check']}
                break  # 변경된 요소를 찾았으므로 반복문 종료
        # 모든 참가자의 체크 상태 확인
        all_checked = all(user.get('user_check') == 'Y' for user in board['user'])
        if all_checked:
            # 모든 참가자가 체크되었을 경우에만 상태를 'end'로 변경
            board['status'] = 'end'

        # 변경된 board를 업데이트
        db.board.update_one({'_id': ObjectId(board_id)}, {'$set': board})

        return jsonify({'message': 'check successfully!', 'user': onuser}), 200
        # return jsonify({'message': 'success'})
    else:
        return jsonify({'message': 'something wrong!'}), 500


# 완료된 haja 소감쓰기
@app.route('/api/board/end/comment', methods=['POST'])

def board_comment():
    # 소감 쓰기 버튼 클릭 시 update comment 칼럼에 댓글 추가 및 사용자 이름 추가
    jwt_token = request.cookies.get('token')

    if not jwt_token:
        # If JWT token is not present in the cookie, return an error response
        return jsonify({'error': 'JWT token is missing'}), 401
    # 완료 버튼 클릭시 update 참가자 체크 & 모든 참가자가 체크 상태일 시 => 게시글의 상태를 완료 상태로 변경
    token = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
    # 입력하고자 하는 user
    user_name = token.get('user_name')

    # 기존 보드의 ID
    board_id = request.form.get('board_id')


    # 입력한 댓글
    comment = request.form.get('comment')

    # 해당 board를 조회
    board = db.board.find_one({'_id': ObjectId(board_id)})

    if board:
        # 기존 review 필드가 있는지 확인
        if 'review' in board:
            review = board['review']
        else:
            review = []

        # 새로운 리뷰 추가
        review.append({'username': user_name, 'comment': comment})

        # board 업데이트
        db.board.update_one({'_id': ObjectId(board_id)}, {'$set': {'review': review}})
        # return redirect(url_for('board_end'))
        return jsonify({'message': 'wirte review successfully!', 'review': review}), 200
    else:
        return jsonify({'message': 'board not found!'}), 500


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
