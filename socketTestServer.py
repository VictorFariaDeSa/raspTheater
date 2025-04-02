from flask import Flask,request,jsonify,Response,abort
from flask_socketio import SocketIO,emit,send
import json
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "123"
socketio = SocketIO(app)

connected_users = {}

with open("videos.json","r") as file:
    video_dict = json.load(file)

@socketio.on("connect")
def handle_connect():
    sid = request.sid
    print(f"Usuário conectado: {sid}")

@socketio.on("register_user")
def handle_register_user(data):
    sid = request.sid
    username = data.get("user", "Usuário Anônimo")
    connected_users[sid] = username
    print(f"Usuário registrado: {username} (sid: {sid})")

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    connected_users.pop(sid, None)
    print(f"Usuário desconectado: {sid}")


@app.route("/",methods=["POST","GET"])
def home():
    socketio.emit("test_message", {"message": "Nova Requisição realizada."})
    return "ok" ,200

@app.route("/get_video_dict")
def get_video():
    return video_dict,200

@app.route("/update_video/",methods=["POST"])
def update_class():
    data = request.get_json()
    video_dict.update(data)
    
    json_object = json.dumps(video_dict, indent=4)
    with open("videos.json", "w") as outfile:
        outfile.write(json_object)
    socketio.emit("update_videos_dict",video_dict)
    return jsonify(video_dict)

@app.route('/video-stream/<videoName>')
def serve_video_stream(videoName):
    path = f'Videos/{videoName}'
    try:
        range_header = request.headers.get('Range', None)
        if not range_header:
            with open(path, 'rb') as video:
                data = video.read()
            return Response(data, mimetype='video/mp4')
        
        range_match = range_header.strip().replace('bytes=', '').split('-')
        start = int(range_match[0])
        end = int(range_match[1]) if range_match[1] else None

        file_size = os.path.getsize(path)
        end = end if end else file_size - 1

        with open(path, 'rb') as video:
            video.seek(start)
            data = video.read(end - start + 1)

        response = Response(data, status=206, mimetype='video/mp4')
        response.headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response.headers['Accept-Ranges'] = 'bytes'
        return response

    except Exception as e:
        abort(500, f'Erro ao processar o vídeo: {str(e)}')

@app.route("/upload_file", methods=["POST"])
def upload_file():
    print(request.files)
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        upload_folder = "Videos"
        filename = file.filename
        file.save(os.path.join(upload_folder, filename))

        return jsonify(video_dict), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete_video/<videoName>", methods=["DELETE"])
def delete_video(videoName):
    try:
        video_path = os.path.join("Videos", videoName)
        if os.path.exists(video_path):
            os.remove(video_path)
            return jsonify({"message": "Video deleted successfully"}), 200
        else:
            return jsonify({"error": "Video not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/change_video/<videoName>", methods=["POST"])
def change_video(videoName):
    socketio.emit("change_video",videoName)
    return jsonify(videoName), 200

if __name__ == "__main__":
    socketio.run(app)