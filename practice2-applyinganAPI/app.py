import os
import requests
import logging
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
API_KEY = "d697c19ef0"
BASE_URL = "https://unidbapi.com/api/university"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return None

def fetch_university_names():
    url = f"{BASE_URL}/search?u=University&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

@app.route('/')
def index():
    universities = fetch_university_names()
    return render_template('index.html', universities=universities)

@app.route('/api/search', methods=['GET'])
def search():
    university_name = request.args.get('searchUniversityName')
    logging.debug(f"Searching for university: {university_name}")
    url = f"{BASE_URL}/search?u={university_name}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        universities = response.json()
        logging.debug(f"Search results: {universities}")
    else:
        universities = []
        logging.error(f"Failed to fetch search results. Status code: {response.status_code}")
    return render_template('search_results.html', universities=universities)

# ------------------------------------------------------------------------------------------------
# Add University POST
@app.route('/add-university', methods=['POST'])
def add_university_prompt():
    university_name = request.form['universityName']
    return render_template('add_university.html', university_name=university_name)

@app.route('/api/create', methods=['POST'])
def create_university():
    data = {
        'name': request.form['name'],
        'description': request.form['description'],
        'country': request.form['country'],
        'city': request.form['city'],
        'altcity': request.form.get('altcity', ''),
        'established': request.form['established'],
        'key': API_KEY
    }

    files = {}
    for key in ['logo', 'icon', 'crest', 'photo']:
        if key in request.files and request.files[key].filename != '':
            file_path = save_file(request.files[key])
            if file_path:
                files[key] = file_path

    data.update(files)
    url = f"{BASE_URL}/create"
    logging.debug(f"Sending data to create university: {data}")
    response = requests.post(url, data=data)

    if response.status_code == 201:
        logging.debug(f"University created successfully: {data['name']}")
        return redirect(url_for('search', searchUniversityName=data['name']))
    else:
        logging.error(f"Failed to create university. Status code: {response.status_code}, Response: {response.text}")
        return redirect(url_for('index'))

@app.route('/api/update', methods=['PUT'])
def update_university():
    # Assuming the update API works similarly and requires a name and the data to update
    data = {
        'name': request.form['universityId'],  # Name used to identify the university
        'new_name': request.form['newUniversityName'],  # Assume API supports name change
        'key': API_KEY
    }
    url = f"{BASE_URL}/update"
    response = requests.put(url, data=data)
    return redirect(url_for('index'))

@app.route('/api/delete', methods=['DELETE'])
def delete_university():
    university_name = request.form['deleteUniversityId']
    url = f"{BASE_URL}/delete?u={university_name}&key={API_KEY}"
    response = requests.delete(url)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
