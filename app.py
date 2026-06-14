import os
import json
import time
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# Storage folders (Temporary storage as no Volume is used)
UPLOAD_FOLDER = 'uploads'
ICON_FOLDER = 'icons'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ICON_FOLDER, exist_ok=True)

# 500MB Upload Limit
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

USER_PASS = "1234"
ADMIN_PASS = "admin"
app_config = {"name": "CKR STORE"}

@app.route('/')
def index():
    files = []
    try:
        for f in os.listdir(UPLOAD_FOLDER):
            stat = os.stat(os.path.join(UPLOAD_FOLDER, f))
            files.append({"name": f, "time": stat.st_mtime})
        files.sort(key=lambda x: x['time'], reverse=True)
    except: pass
    return render_template('index.html', name=app_config['name'], files=files, ts=int(time.time()))

@app.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if request.form.get('password') == USER_PASS and file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return jsonify({"status": "ok"})
    return "Error", 401

@app.route('/set_icon', methods=['POST'])
def set_icon():
    icon = request.files.get('icon')
    filename = request.form.get('filename')
    if request.form.get('password') == ADMIN_PASS and icon:
        icon.save(os.path.join(ICON_FOLDER, filename + ".png"))
        return jsonify({"status": "ok"})
    return "Error", 401

@app.route('/get_icon/<filename>')
def get_icon(filename):
    p = os.path.join(ICON_FOLDER, filename + ".png")
    if os.path.exists(p): return send_from_directory(ICON_FOLDER, filename + ".png")
    return "No Icon", 404

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/delete', methods=['POST'])
def delete():
    data = request.json
    if data.get('password') == USER_PASS:
        try: os.remove(os.path.join(UPLOAD_FOLDER, data['name']))
        except: pass
        try: os.remove(os.path.join(ICON_FOLDER, data['name'] + ".png"))
        except: pass
        return jsonify({"status": "ok"})
    return "Error", 401

@app.route('/rename_app', methods=['POST'])
def rename_app():
    data = request.json
    if data.get('password') == ADMIN_PASS:
        app_config['name'] = data['name']
        return jsonify({"status": "ok"})
    return "Error", 401

if __name__ == '__main__':
    # Railway looks for PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)