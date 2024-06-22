import os
import http.client
import json
import mimetypes
from codecs import encode
from flask import Flask, render_template, request, redirect, url_for, flash, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages
API_KEY = "live_rrKWnYRKic9aWlzfu5ZuCC3kgOFKbZraoR47jVVfulr94Vrfo5fLwSKzKqDxrAZw"
BASE_URL = "api.thecatapi.com"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return file_path
    return None

def fetch_breeds():
    conn = http.client.HTTPSConnection(BASE_URL)
    headers = {'x-api-key': API_KEY}
    conn.request("GET", "/v1/breeds", headers=headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    if res.status == 200:
        return json.loads(data)
    return []

@app.route('/')
def index():
    breeds = fetch_breeds()
    return render_template('index.html', breeds=breeds)

@app.route('/search', methods=['GET'])
def search():
    origin = request.args.get('origin')
    conn = http.client.HTTPSConnection(BASE_URL)
    headers = {'x-api-key': API_KEY}
    conn.request("GET", f"/v1/images/search?breed_ids={origin}&limit=10", headers=headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    if res.status == 200:
        images = json.loads(data)
    else:
        images = []
    return render_template('search_results.html', images=images)

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            file_path = save_file(file)
            conn = http.client.HTTPSConnection(BASE_URL)
            boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
            dataList = []
            dataList.append(encode('--' + boundary))
            dataList.append(encode(f'Content-Disposition: form-data; name="file"; filename="{file.filename}"'))
            fileType = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            dataList.append(encode(f'Content-Type: {fileType}'))
            dataList.append(encode(''))

            with open(file_path, 'rb') as f:
                dataList.append(f.read())
            dataList.append(encode(f'--{boundary}--'))
            dataList.append(encode(''))

            body = b'\r\n'.join(dataList)
            headers = {
                'x-api-key': API_KEY,
                'Content-type': f'multipart/form-data; boundary={boundary}'
            }

            conn.request("POST", "/v1/images/upload", body, headers)
            res = conn.getresponse()
            data = res.read()
            conn.close()

            # Debugging: Print response details
            print(f"Response Status: {res.status}")
            print(f"Response Text: {data.decode('utf-8')}")

            if res.status == 201:
                flash('Image uploaded successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash(f'Failed to upload image. Status code: {res.status}', 'error')
    return render_template('upload.html')

@app.route('/update', methods=['GET', 'POST'])
def update_image():
    if request.method == 'POST':
        image_id = request.form['image_id']
        file = request.files['file']
        if file and allowed_file(file.filename):
            file_path = save_file(file)
            conn = http.client.HTTPSConnection(BASE_URL)
            boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
            dataList = []
            dataList.append(encode('--' + boundary))
            dataList.append(encode(f'Content-Disposition: form-data; name="file"; filename="{file.filename}"'))
            fileType = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            dataList.append(encode(f'Content-Type: {fileType}'))
            dataList.append(encode(''))

            with open(file_path, 'rb') as f:
                dataList.append(f.read())
            dataList.append(encode(f'--{boundary}--'))
            dataList.append(encode(''))

            body = b'\r\n'.join(dataList)
            headers = {
                'x-api-key': API_KEY,
                'Content-type': f'multipart/form-data; boundary={boundary}'
            }

            conn.request("PUT", f"/v1/images/{image_id}", body, headers)
            res = conn.getresponse()
            data = res.read()
            conn.close()

            # Debugging: Print response details
            print(f"Response Status: {res.status}")
            print(f"Response Text: {data.decode('utf-8')}")

            if res.status == 200:
                flash('Image updated successfully!', 'success')
                return redirect(url_for('view_image', image_id=image_id))
            else:
                flash(f'Failed to update image. Status code: {res.status}', 'error')
    return render_template('update.html')

@app.route('/delete', methods=['GET', 'POST'])
def delete_image():
    if request.method == 'POST':
        image_id = request.form['image_id']

        conn = http.client.HTTPSConnection(BASE_URL)
        headers = {'x-api-key': API_KEY}

        conn.request("DELETE", f"/v1/images/{image_id}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()

        # Debugging: Print response details
        print(f"Response Status: {res.status}")
        print(f"Response Text: {data.decode('utf-8')}")

        if res.status == 200:
            flash('Image deleted successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Failed to delete image. Status code: {res.status}', 'error')
    return render_template('delete.html')

@app.route('/view/<image_id>', methods=['GET'])
def view_image(image_id):
    conn = http.client.HTTPSConnection(BASE_URL)
    headers = {'x-api-key': API_KEY}
    conn.request("GET", f"/v1/images/{image_id}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    if res.status == 200:
        image_data = json.loads(data)
        image_url = image_data.get('url')
        return render_template('view_image.html', image_url=image_url)
    else:
        flash(f'Failed to retrieve image. Status code: {res.status}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
