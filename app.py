import os
import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the-game-secure-key-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_room')
def on_create(data):
    room_id = str(random.randint(1000, 9999))
    while room_id in rooms:
        room_id = str(random.randint(1000, 9999))
    rooms[room_id] = {
        "players": {request.sid: data['name']},
        "host": request.sid,
        "started": False,
        "order": [],
        "current_idx": 0,
        "deck": list(range(2, 100)),
        "piles": {"a1": 1, "a2": 1, "d1": 100, "d2": 100}
    }
    random.shuffle(rooms[room_id]["deck"])
    join_room(room_id)
    emit('room_created', {"room_id": room_id, "players": list(rooms[room_id]["players"].values())})

@socketio.on('join_room')
def on_join(data):
    room_id = data.get('room_id')
    name = data.get('name')
    if room_id in rooms:
        join_room(room_id)
        rooms[room_id]["players"][request.sid] = name
        emit('player_joined', {"players": list(rooms[room_id]["players"].values())}, room=room_id)
    else:
        emit('error', {"message": "部屋が見つかりません。"})

@socketio.on('request_initial_cards')
def on_request_cards(data):
    room_id = data.get('room_id')
    if room_id in rooms:
        room = rooms[room_id]
        num_players = len(room["players"])
        max_hand = 7 if num_players == 2 else (6 if num_players >= 3 else 8)
        hands = {}
        for sid, name in room["players"].items():
            hands[name] = [room["deck"].pop() for _ in range(max_hand)]
        emit('distribute_initial_cards', {
            "hands": hands, 
            "deck_count": len(room["deck"]), 
            "num_players": num_players,
            "player_list": list(room["players"].values())
        }, room=room_id)

@socketio.on('confirm_first_player')
def on_confirm(data):
    room_id = data.get('room_id')
    if room_id in rooms:
        player_names = list(rooms[room_id]["players"].values())
        first_player = data.get('firstPlayer')
        others = [n for n in player_names if n != first_player]
        random.shuffle(others)
        order = [first_player] + others
        rooms[room_id]["order"] = order
        rooms[room_id]["started"] = True
        emit('start_game_with_order', {"order": order}, room=room_id)

@socketio.on('sync_move')
def on_sync(data):
    room_id = data.get('room_id')
    rooms[room_id]["piles"][data['pileId']] = data['val']
    emit('update_board', data, room=room_id)

@socketio.on('draw_cards')
def on_draw(data):
    room_id = data.get('room_id')
    count = data.get('count')
    if room_id in rooms:
        room = rooms[room_id]
        drawn = [room["deck"].pop() for _ in range(min(count, len(room["deck"])))]
        emit('receive_drawn_cards', {"cards": drawn, "deck_count": len(room["deck"]), "player_name": data.get('name')})
        emit('update_deck_count', {"deck_count": len(room["deck"])}, room=room_id, include_self=False)

@socketio.on('next_turn')
def on_next(data):
    emit('update_turn', {"nextIdx": data['nextIdx']}, room=data['room_id'])

@socketio.on('game_end')
def on_game_end(data):
    emit('receive_game_end', data, room=data['room_id'])

# スタンプ転送用
@socketio.on('send_stamp')
def on_stamp(data):
    emit('receive_stamp', data, room=data['room_id'])

@socketio.on('send_signal')
def on_signal(data):
    emit('receive_signal', data, room=data['room_id'])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)import os
import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the-game-secure-key-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_room')
def on_create(data):
    room_id = str(random.randint(1000, 9999))
    while room_id in rooms:
        room_id = str(random.randint(1000, 9999))
    rooms[room_id] = {
        "players": {request.sid: data['name']},
        "host": request.sid,
        "started": False,
        "order": [],
        "current_idx": 0,
        "deck": list(range(2, 100)),
        "piles": {"a1": 1, "a2": 1, "d1": 100, "d2": 100}
    }
    random.shuffle(rooms[room_id]["deck"])
    join_room(room_id)
    emit('room_created', {"room_id": room_id, "players": list(rooms[room_id]["players"].values())})

@socketio.on('join_room')
def on_join(data):
    room_id = data.get('room_id')
    name = data.get('name')
    if room_id in rooms:
        join_room(room_id)
        rooms[room_id]["players"][request.sid] = name
        emit('player_joined', {"players": list(rooms[room_id]["players"].values())}, room=room_id)
    else:
        emit('error', {"message": "部屋が見つかりません。"})

@socketio.on('request_initial_cards')
def on_request_cards(data):
    room_id = data.get('room_id')
    if room_id in rooms:
        room = rooms[room_id]
        num_players = len(room["players"])
        max_hand = 7 if num_players == 2 else (6 if num_players >= 3 else 8)
        hands = {}
        for sid, name in room["players"].items():
            hands[name] = [room["deck"].pop() for _ in range(max_hand)]
        emit('distribute_initial_cards', {
            "hands": hands, 
            "deck_count": len(room["deck"]), 
            "num_players": num_players,
            "player_list": list(room["players"].values())
        }, room=room_id)

@socketio.on('confirm_first_player')
def on_confirm(data):
    room_id = data.get('room_id')
    if room_id in rooms:
        player_names = list(rooms[room_id]["players"].values())
        first_player = data.get('firstPlayer')
        others = [n for n in player_names if n != first_player]
        random.shuffle(others)
        order = [first_player] + others
        rooms[room_id]["order"] = order
        rooms[room_id]["started"] = True
        emit('start_game_with_order', {"order": order}, room=room_id)

@socketio.on('sync_move')
def on_sync(data):
    room_id = data.get('room_id')
    rooms[room_id]["piles"][data['pileId']] = data['val']
    emit('update_board', data, room=room_id)

@socketio.on('draw_cards')
def on_draw(data):
    room_id = data.get('room_id')
    count = data.get('count')
    if room_id in rooms:
        room = rooms[room_id]
        drawn = [room["deck"].pop() for _ in range(min(count, len(room["deck"])))]
        emit('receive_drawn_cards', {"cards": drawn, "deck_count": len(room["deck"]), "player_name": data.get('name')})
        emit('update_deck_count', {"deck_count": len(room["deck"])}, room=room_id, include_self=False)

@socketio.on('next_turn')
def on_next(data):
    emit('update_turn', {"nextIdx": data['nextIdx']}, room=data['room_id'])

@socketio.on('game_end')
def on_game_end(data):
    emit('receive_game_end', data, room=data['room_id'])

# スタンプ転送用
@socketio.on('send_stamp')
def on_stamp(data):
    emit('receive_stamp', data, room=data['room_id'])

@socketio.on('send_signal')
def on_signal(data):
    emit('receive_signal', data, room=data['room_id'])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
