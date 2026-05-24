from flask import Flask, Response, render_template, jsonify, request
from flask_socketio import SocketIO
import logging

def create_app(camera_stream, list_objects, object_tracked, keys, keys_lock):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    socketio = SocketIO(app, async_mode='threading', cors_allowed_origins='*')

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    @app.route('/video_feed')
    def video_feed():
        return Response(
            camera_stream.generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )

    @app.route('/get_list_objects')
    def get_list_objects():
        return jsonify(list_objects)

    @app.route('/tracking_object', methods=['POST'])
    def tracking_object():
        data = request.get_json(silent=True) or {}
        object_id = data.get('object_id')
        object_class_name = data.get('class_name')

        if object_id is None or object_class_name is None:
            return jsonify({"ok": False, "error": "Missing object_id or class_name"}), 400

        object_tracked['enabled'] = True
        object_tracked['object_id'] = object_id
        object_tracked['class_name'] = object_class_name

        print(f"Object received: {object_tracked['enabled']}, {object_id}, {object_class_name}")
        return jsonify({"ok": True, "target": object_tracked})

    @app.route('/stop_tracking_rov', methods=['POST'])
    def stop_tracking_rov():
        data = request.get_json(silent=True) or {}
        object_id = data.get('object_id')
        object_class_name = data.get('class_name')

        if object_id is None or object_class_name is None:
            return jsonify({"ok": False, "error": "Missing object_id or class_name"}), 400

        print(f"Stopping Object: {object_id}, {object_class_name}")

        object_tracked['enabled'] = False
        object_tracked['object_id'] = object_id
        object_tracked['class_name'] = object_class_name

        return jsonify({"ok": True, "target": object_tracked})

    @socketio.on("manual_movement")
    def manual_movement(data):
        with keys_lock:
            keys[0] = 1 if data.get("w") else 0
            keys[1] = 1 if data.get("a") else 0
            keys[2] = 1 if data.get("s") else 0
            keys[3] = 1 if data.get("d") else 0
        return {"SERVER RECEIVED": keys}

    @app.route('/')
    def index():
        return render_template("index.html")

    return app, socketio