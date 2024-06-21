from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

# Initialize the Flask application
app = Flask(__name__)

API_KEY = "DEMO_KEY"

# Define a route to fetch and display the list of food items
@app.route('/')
def index():
    api_url = f"https://api.nal.usda.gov/fdc/v1/foods/list?api_key={API_KEY}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        food_items = response.json()
    except requests.RequestException as e:
        return f"Error fetching data from the API: {str(e)}", 500

    # Render the HTML template and pass the food items to it
    return render_template('index.html', food_items=food_items)

# Define a route to fetch and display details of a specific food item
@app.route('/food/<int:fdcId>')
def food_detail(fdcId):
    api_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdcId}?api_key={API_KEY}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        food_details = response.json()
        print(food_details)  
    except requests.RequestException as e:
        return f"Error fetching data from the API: {str(e)}", 500

    return render_template('detail.html', food=food_details)


# Run the Flask application
if __name__ == '__main__':
    app.run()



