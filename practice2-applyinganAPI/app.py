from flask import Flask, request, jsonify, render_template, redirect, url_for
import requests

app = Flask(__name__)
API_KEY = "d697c19ef0"
BASE_URL = "https://unidbapi.com/api/university"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search():
    university_name = request.args.get('searchUniversityName')
    url = f"{BASE_URL}/search?u={university_name}&key={API_KEY}"
    response = requests.get(url)
    universities = response.json() if response.status_code == 200 else []
    return render_template('search_results.html', universities=universities)

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
        'altcity': request.form['altcity'],
        'established': request.form['established'],
        'key': API_KEY
    }
    url = f"{BASE_URL}/create"
    response = requests.post(url, data=data)
    return redirect(url_for('index'))

@app.route('/api/update', methods=['POST'])
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

@app.route('/api/delete', methods=['POST'])
def delete_university():
    university_name = request.form['deleteUniversityId']
    url = f"{BASE_URL}/delete?u={university_name}&key={API_KEY}"
    response = requests.delete(url)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
