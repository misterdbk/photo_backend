from flask import Flask, request, jsonify, send_from_directory
import os, shutil, json
from datetime import datetime

app = Flask(__name__)
PHOTO_ROOT = 'photos'
SELECTED_ROOT = 'selected'
CLIENTS_FILE = 'server/clients.json'

def load_clients():
    with open(CLIENTS_FILE, 'r') as f:
        return json.load(f)

@app.route('/api/photos')
def list_photos():
    client = request.args.get('client')
    folder = os.path.join(PHOTO_ROOT, client)
    if not os.path.exists(folder):
        return jsonify([])
    return jsonify(os.listdir(folder))

@app.route('/photos/<client>/<filename>')
def serve_photo(client, filename):
    return send_from_directory(os.path.join(PHOTO_ROOT, client), filename)

@app.route('/api/select', methods=['POST'])
def select_photo():
    data = request.json
    client = data['client']
    photo = data['photo']
    src = os.path.join(PHOTO_ROOT, client, photo)
    dest_folder = os.path.join(SELECTED_ROOT, client)
    os.makedirs(dest_folder, exist_ok=True)
    shutil.copy(src, os.path.join(dest_folder, photo))
    return 'selected'

@app.route('/api/deselect', methods=['POST'])
def deselect_photo():
    data = request.json
    client = data['client']
    photo = data['photo']
    path = os.path.join(SELECTED_ROOT, client, photo)
    if os.path.exists(path):
        os.remove(path)
    return 'deselected'

@app.route('/dashboard')
def dashboard():
    return send_from_directory('www', 'dashboard.html')

@app.route('/client')
def client_view():
    return send_from_directory('www', 'client.html')

@app.route('/api/clients')
def get_clients():
    return jsonify(load_clients())

@app.route('/api/add-client', methods=['POST'])
def add_client():
    data = request.json
    clients = load_clients()
    name = data['name']
    clients[name] = {
        "created": str(datetime.today().date()),
        "expires": data.get("expires", ""),
        "folder": name
    }
    with open(CLIENTS_FILE, 'w') as f:
        json.dump(clients, f)
    os.makedirs(os.path.join(PHOTO_ROOT, name), exist_ok=True)
    return 'client added'

if __name__ == '__main__':
    app.run(port=8080)
