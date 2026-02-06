import os
import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
# セキュリティのためのキー設定
app.config['SECRET_KEY'] = 'the-game-secret-key-12345'

# SocketIOの初期化。Renderなどの外部サーバーで動かすためにcorsを許可します
socketio = SocketIO(app, cors_allowed_origins="*")

# サーバー側で全ルームの状態を管理
rooms = {}

@app.route('/')
def index():
    """メイン画面（index.html）を表示"""
    return render_template('index.html')

@socketio.on('create_room')
def on_create():
    """新しい部屋を作成し、作成者をホストとして登録"""
    room_id = str(random.randint(1000, 9999))
    # すでに存在する部屋番号を避ける
    while room_id in rooms:
        room_id = str(random.randint(1000, 9999))
    
    rooms[room_id] = {
        "players": [request.sid],
        "host": request.sid,
        "started": False,
        "piles": {"a1": 1, "a2": 1, "d1": 100, "d2": 100}
    }
    join_room(room_id)
    # 部屋ができたことを本人に通知
    emit('room_created', {"room_id": room_id, "player_count": 1})

@socketio.on('join_room')
def on_join(data):
    """既存の部屋に合流"""
    room_id = data.get('room_id')
    if room_id in rooms:
        if rooms[room_id]["started"]:
            emit('error', {"message": "そのゲームは既に開始されています。"})
            return
        
        join_room(room_id)
        rooms[room_id]["players"].append(request.sid)
        # 部屋にいる全員に人数が増えたことを通知
        emit('player_joined', {"player_count": len(rooms[room_id]["players"])}, room=room_id)
    else:
        emit('error', {"message": "部屋番号が見つかりません。"})

@socketio.on('start_game')
def on_start(data):
    """ホストが開始ボタンを押した時の処理"""
    room_id = data.get('room_id')
    if room_id in rooms and rooms[room_id]["host"] == request.sid:
        rooms[room_id]["started"] = True
        num_players = len(rooms[room_id]["players"])
        # 全員にゲーム開始を合図（人数情報を送る）
        emit('game_started', {"num_players": num_players}, room=room_id)

@socketio.on('sync_move')
def on_sync(data):
    """カードが置かれた動きを他のプレイヤーに同期"""
    room_id = data.get('room_id')
    # 置いた本人以外にデータを送信して、盤面を更新させる
    emit('update_board', data, room=room_id, include_self=False)

if __name__ == '__main__':
    # Render環境ではPORT環境変数が指定されるため、それに従う
    port = int(os.environ.get("PORT", 5000))
    # 外部アクセスを許可するために host='0.0.0.0' を指定
    socketio.run(app, host='0.0.0.0', port=port)