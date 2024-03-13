from bson import ObjectId
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import datetime
import jwt
import certifi
from flask_restx import Api, Resource, reqparse


from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import get_jwt, jwt_required,JWTManager,create_access_token

app = Flask(__name__)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'
SECRET_KEY = 'your_secret_key123123'
jwt=JWTManager(app)


# MongoDB 연결
client = MongoClient('mongodb+srv://sparta:jungle@cluster0.5ue2fmm.mongodb.net/?retryWrites=true&w=majority')
db = client.haja  # 여기에 본인의 MongoDB 데이터베이스 이름을 넣으세요


# 시작 페이지
@app.route('/')
def index_page():
    return render_template('index.html')


# 메인 haja 페이지 이동
@app.route('/api/board/main', methods=['GET'])
# @jwt_required()
def board_main():

    # 모든 게시글 가져오기
    all_results = list(db.board.find({}))

    # 진행상태는 아직 안정해졌고, 모집상태가 on인것만 반환
    filtered_results = []
    for item in all_results:
        if item.get('status') == '' and item.get('meet') == 'on':
            filtered_results.append(item)

    return render_template('main_haja.html', result=filtered_results)

# 내가 만든 haja 페이지 이동
@app.route('/api/board/my', methods=['GET'])
@jwt_required()
def board_my():
    user_name=request.form.get('user_name')
    # 모든 게시글 가져오기
    all_results = list(db.board.find({}))

    # 진행상태는 안정해졌고(''), 모집상태가 on이고, 글쓴 host가 user_name인것만 반환
    filtered_results = []
    for item in all_results:
        for user in item.get('user'):
            if item.get('status') == '' and item.get('meet') == 'on' and user.get('user_role')=='host' and user.get('user_name')==user_name:
                filtered_results.append(item)
    return render_template('my_haja.html', result=filtered_results)


# 진행중인 haja 페이지 이동
@app.route('/api/board/ongo', methods=['GET'])
@jwt_required()
def board_ongo():
    # 모든 게시글 가져오기
    all_results = list(db.board.find({}))

    # 진행상태는  ongo, 모집상태가 off인것만 반환
    filtered_results = []
    for item in all_results:
        if item.get('status') == '' and item.get('meet') == 'on':
            filtered_results.append(item)
    return render_template('ongo_haja.html', result=filtered_results)


# 완료된 haja 페이지 이동
@app.route('/api/board/end', methods=['GET'])
@jwt_required()
def board_end():
    # 모든 게시글 가져오기
    all_results = list(db.board.find({}))

    # 진행상태는 end이고, 모집상태가 off인것만 반환
    filtered_results = []
    for item in all_results:
        if item.get('status') == 'end' and item.get('meet') == 'off':
            filtered_results.append(item)
    return render_template('end_haja.html', result=filtered_results)


# 로그인
@app.route('/login', methods=['POST'])
def login():
    # 클라이언트에서 제출한 사용자 이름과 비밀번호 가져오기
    user_email = request.json.get('email')
    password = request.json.get('password')

    #
    # user_email = auth['email']
    # password = auth['password']

    # MongoDB에서 사용자 정보 조회
    user = db.users.find_one({'email': user_email})

    if user and check_password_hash(user['password'], password):  # 비밀번호 해싱 체크

        # JWT 토큰 생성 및 사용자 정보 포함
        # token = jwt.encode({'user': user['user_name'], 'email': user['email'],
        #                     'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, SECRET_KEY)
        token=create_access_token(identity=user['email'],expires_delta=datetime.timedelta(minutes=30))
        # 토큰을 응답으로 반환
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

        # 사용자 정보 MongoDB에 저장
        db.users.insert_one({'user_name': user_name, 'email': user_email, 'password': password})

        # 회원가입 성공시 메시지 반환
        return jsonify({'message': 'User registered successfully', 'user_name': user_name})



    return render_template('sign_up.html')


# 게시글 검색
@app.route('/api/board/search', methods=['GET'])
@jwt_required()
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
# @jwt_required()
def board_main_join():
    # 참가 버튼 클릭시 update 참여 인원+1, 참가자 추가

    # 사용자 정보 가져오기
    user_name = request.form['user_name']
    user_role = request.form['user_role']
    user_check = request.form['user_check']

    user = {'user_name': user_name, 'user_role': user_role, 'user_check': user_check}

    # 기존 보드의 ID
    board_id = request.form.get('board_id')

    # 기존 보드를 찾음
    existing_board = db.board.find_one({'_id': ObjectId(board_id)})
    if existing_board:
        # 기존 보드에 유저 추가
        existing_board['user'].append(user)
        existing_board['status']='ongo'
        existing_board['meet']='off'

        # 업데이트된 보드를 저장
        db.board.update_one({'_id': board_id}, {'$set': existing_board})

        return redirect(url_for('board_main'))
    else:
        return jsonify({'message': 'Board not found.'}), 500


# haja 등록
@app.route('/api/board/regi', methods=['POST'])
# @jwt_required()
def regi_board():
    # 사용자 정보 가져오기

    user_name = request.form['user_name']
    user_role = request.form['user_role']
    user_check = request.form['user_check']

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

    if result.inserted_id:
        return jsonify({'message': "register board successfully!", 'board_id': result.inserted_id}), 200
    else:
        return jsonify({'message': "register board fail!"}), 500

#내가 만든 haja 마감
@app.route('/api/board/my/close',methods=['POST'])
@jwt_required()
def close_board():
    board_id=request.form.get('board_id')
    db.board.update_one({'_id': ObjectId(board_id)},{'$set': {'meet': 'off','status': 'ongo'}})
    return redirect(url_for('board_my'))




# 내가 만든 haja 수정
@app.route('/api/board/my/update', methods=['POST'])
@jwt_required()
def update_board():
    # 클라이언트로부터 폼 데이터 추출
    when = request.form.get('when')
    where = request.form.get('where')
    what = request.form.get('what')
    content = request.form.get('content')
    max_num = int(request.form.get('max')) if request.form.get('max') else None

    # 기존 보드의 ID
    board_id = request.form.get('board_id')

    # 기존 보드 수정
    result = db.board.update_one({'_id': ObjectId(board_id)}, {
        '$set': {'when': when, 'where': where, 'what': what, 'content': content, 'max_num': max_num}})

    if result.modified_count > 0:
        return jsonify({'message': "update board successfully!", 'board_id': result.inserted_id}), 200
    else:
        return jsonify({'message': "update board fail!"}), 500


# 내가 만든 haja 삭제
@app.route('/api/board/my/delete', methods=['POST'])
@jwt_required()
def delete_board():
    board_id = request.form.get('board_id')
    result = db.board.delete_one({'_id': ObjectId(board_id)})

    if result.deleted_count:
        return redirect(url_for('board_my'))
    else:
        return jsonify({'message': 'can not delete board!'}), 500


# 진행중인 haja 완료
@app.route('/api/board/ongo/check', methods=['POST'])
@jwt_required()
def board_check():
    # 완료 버튼 클릭시 update 참가자 체크 & 모든 참가자가 체크 상태일 시 => 게시글의 상태를 완료 상태로 변경

    # 기존 보드의 ID
    board_id = request.form.get('board_id')

    # 완료 하고자 하는 user
    user_name = request.form.get('user_name')

    # 해당 board를 조회
    board = db.board.find_one({'_id': ObjectId(board_id)})

    if board:
        # user 배열에서 user_name이 일치하는 요소를 찾음
        for user in board['user']:
            if user['user_name'] == user_name:
                # user_check 값을 변경
                user['user_check'] = 'Y'

                break  # 변경된 요소를 찾았으므로 반복문 종료
        # 모든 참가자의 체크 상태 확인
        all_checked = all(user.get('user_check') == 'Y' for user in board['user'])
        if all_checked:
            # 모든 참가자가 체크되었을 경우에만 상태를 'end'로 변경
            board['status'] = 'end'

        # 변경된 board를 업데이트
        db.board.update_one({'_id': ObjectId(board_id)}, {'$set': board})

        return redirect(url_for('board_ongo'))
        # return jsonify({'message': 'success'})
    else:
        return jsonify({'something wrong!'}), 500


# 완료된 haja 소감쓰기
@app.route('/api/board/end/comment', methods=['POST'])
@jwt_required()
def board_comment():
    # 소감 쓰기 버튼 클릭 시 update comment 칼럼에 댓글 추가 및 사용자 이름 추가

    # 기존 보드의 ID
    board_id = request.form.get('board_id')

    # 완료 하고자 하는 user
    user_name = request.form.get('user_name')

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
        return redirect(url_for('board_end'))
    else:
        return jsonify({'message': 'board not found!'}), 500


if __name__ == '__main__':
    app.run()
