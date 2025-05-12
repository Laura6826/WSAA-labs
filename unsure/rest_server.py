# WSAA-project: Web Services and Applications.
# Main Flask application
# Author: Laura Lyons

from flask import Flask, request, jsonify, render_template
from schema.schema import CarParkSchema, OpeningHoursSchema
import requests
import logging

app = Flask(__name__, static_folder='static')

# External API details
API_URL = "https://data.corkcity.ie/en_GB/api/3/action/datastore_search_sql"
RESOURCE_ID = "f4677dac-bb30-412e-95a8-d3c22134e3c0"

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Check if the API is reachable; http://127.0.0.1:5000/
@app.route('/')
def index():
    logging.debug("Serving the Parking Checker HTML file.")
    return render_template('parking_checker.html')  # Ensure the file is in the 'templates' folder

# Fetch all records (Read)
# curl -X GET http://127.0.0.1:5000/api/fetch
@app.route('/api/fetch', methods=['GET'])
def fetch_parking_data():
    sql_query = f"""
    SELECT * FROM "{RESOURCE_ID}" 
    """
    try:
        logging.debug("SQL Query Sent: %s", sql_query)
        params = {"sql": sql_query}

        # Make the API request
        response = requests.get(API_URL, params=params, timeout=10)
        logging.debug(f"Response Status: {response.status_code}")
        logging.debug(f"Response Data: {response.text}")

        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            records = data.get("result", {}).get("records", [])
            logging.debug(f"Parsed Records: {records}")
            return jsonify(records), 200
        else:
            logging.error(f"API returned HTTP {response.status_code}: {response.text}")
            return jsonify({"error": f"Failed to fetch data. HTTP Status Code: {response.status_code}"}), response.status_code
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        return jsonify({"error": str(e)}), 500

# Fetch a single record by ID (Read)
# curl -X GET http://127.0.0.1:5000/api/parking/1
@app.route('/api/parking/<int:idd>', methods=['GET'])
def fetch_parking_by_id(idd):
    logging.debug(f"Fetching parking data for ID: {idd}")
    try:
        # Define query parameters
        params = {"resource_id": RESOURCE_ID, "q": {"idd": idd}}
        logging.debug(f"Query Params: {params}")

        # Make the API request
        response = requests.get(API_URL, params=params)
        logging.debug(f"Response Status: {response.status_code}")
        logging.debug(f"Response Data: {response.text}")

        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            records = data.get("result", {}).get("records", [])
            logging.debug(f"Parsed Record: {records}")
            if not records:
                return jsonify({"error": "Parking record not found"}), 404
            return jsonify(records[0]), 200
        else:
            logging.error(f"API returned HTTP {response.status_code}: {response.text}")
            return jsonify({"error": f"Failed to fetch data. HTTP Status Code: {response.status_code}"}), response.status_code
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        return jsonify({"error": str(e)}), 500

# Create a new parking record (Create)
# curl -X POST -H "Content-Type: application/json" -d '{"name": "New Parking", "spaces_available": 50}' http://127.0.0.1:5000/api/parking
@app.route('/api/parking', methods=['POST'])
def create_parking():
    try:
        logging.debug("Simulating creation of a parking record.")
        data = request.json
        logging.debug(f"Data Received: {data}")
        return jsonify({"message": "Creation is not supported in external API. Simulated record:", "data": data}), 201
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        return jsonify({"error": str(e)}), 500

# Update a parking record (Update)
# curl -X DELETE http://127.0.0.1:5000/api/parking/1
@app.route('/api/parking/<int:idd>', methods=['PUT'])
def update_parking(idd):
    try:
        logging.debug("Simulating update of a parking record.")
        data = request.json
        logging.debug(f"Data Received: {data}")
        data['idd'] = idd
        logging.debug(f"Simulated Updated Data: {data}")
        return jsonify({"message": "Update is not supported in external API. Simulated update:", "data": data}), 200
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        return jsonify({"error": str(e)}), 500

# Delete a parking record (Delete)
# curl -X DELETE http://127.0.0.1:5000/api/parking/1
@app.route('/api/parking/<int:idd>', methods=['DELETE'])
def delete_parking(idd):
    try:
        logging.debug("Simulating deletion of a parking record.")
        logging.debug(f"ID to Delete: {idd}")
        return jsonify({"message": f"Deletion is not supported in external API. Simulated deletion of ID: {idd}"}), 200
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logging.debug("Starting the Flask server...")
    app.run(debug=True)
