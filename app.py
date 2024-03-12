from flask import Flask, render_template, request

app = Flask(__name__)


# 시작 페이지
@app.route('/')
def index_page():
    return render_template('index.html')


# 로그인
@app.route('/login', methods=['POST'])
def login():
    # 로그인 인증 로직 및 인증 성공시 jwt 발급 로직
    # 나머지 api에 대해서 전부 @jwt_required() 붙여줘야 함
    # 또한 성공시에는 main_haja페이지로 반환
    return


# 회원 가입
@app.route('/api/sign_up', methods=['GET', 'POST'])
def sign_up():
    # 회원 가입 요청일 때
    if request.method == 'POST':
        # 회원 가입 로직 작성
        return
    return render_template('sign_up.html')

# 게시글 검색
@app.route('/api/board/search', methods=['GET'])
def search_board():
    # 시간, 장소, 내용에 해당 텍스트가 포함되는 모든 문서 검색

    return

# 메인 haja 페이지 이동
@app.route('/api/board/main', methods=['GET'])
def board_main():
    return render_template('main_haja.html')


# 메인 haja 페이지에서 참가 버튼 클릭시
@app.route('/api/board/main/join', methods=['POST'])
def board_main_join():
    # 참가 버튼 클릭시 update 참여 인원+1, 참가자 추가
    return


# haja 등록
@app.route('/api/board/regi', methods=['GET', 'POST'])
def regi_board():
    # 게시글 등록일 때
    if request.method == 'POST':
        return
    return render_template('regi_haja.html')

# 내가 만든 haja 페이지 이동
@app.route('/api/board/my', methods=['GET'])
def board_my():
    return render_template('my_haja.html')


# 내가 만든 haja 수정
@app.route('/api/board/my/update', methods=['GET', 'POST'])
def update_board():
    # 게시글 수정일 때
    if request.method == 'POST':
        return
    return render_template('update_haja.html')

# 내가 만든 haja 삭제
@app.route('/api/board/delete', methods=['POST'])
def delete_board():
    # 게시글 삭제 로직
    return


# 진행중인 haja 페이지 이동
@app.route('/api/board/ongo', methods=['GET'])
def board_ongo():
    return render_template('ongo_haja.html')

# 진행중인 haja 완료
@app.route('/api/board/check', methods=['POST'])
def board_check():
    #완료 버튼 클릭시 update 참가자 체크 & 모든 참가자가 체크 상태일 시 => 게시글의 상태를 완료 상태로 변경
    return


# 완료된 haja 페이지 이동
@app.route('/api/board/end', methods=['GET'])
def board_end():
    return render_template('end_haja.html')

# 완료된 haja 소감쓰기
@app.route('/api/board/end/comment', methods=['POST'])
def board_comment():
    #소감 쓰기 버튼 클릭 시 update comment 칼럼에 댓글 추가 및 사용자 이름 추가
    return


if __name__ == '__main__':
    app.run()
