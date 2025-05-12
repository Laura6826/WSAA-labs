from flask import Flask, request, jsonify, render_template
from marshmallow import ValidationError
import requests
import logging
from dao.car_parks_dao import CarParksDAO
from dao.opening_hours_dao import OpeningHoursDAO
from dao.live_spaces_dao import LiveSpacesDAO
from schema.schema import CarParkSchema, OpeningHoursSchema

app = Flask(__name__, template_folder="templates")

# DAO instances
car_parks_dao = CarParksDAO()
opening_hours_dao = OpeningHoursDAO()
live_spaces_dao = LiveSpacesDAO()

if not car_parks_dao:
    logging.error("❌ CarParksDAO is missing!")
    raise RuntimeError("DAO objects not initialized correctly.")

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Root endpoint
# Check if the API is reachable; http://127.0.0.1:5000/
@app.route("/")
def hello():
    return "Hello, world!"

# Root endpoint
# Check if the API is reachable; http://127.0.0.1:5000/
@app.route("/")
def home():
    return render_template("parking_checker.html")

# API endpoint to fetch live parking availability
# Check if the API is reachable; http://
@app.route('/api/parking-availability', methods=['GET'])
def fetch_parking_availability():
    try:
        logging.debug("✅ API request received at /api/parking-availability")

        # Validate DAOs exist before proceeding
        if not car_parks_dao or not opening_hours_dao:
            logging.error("❌ DAO objects are missing! Ensure they are initialized properly.")
            return jsonify({"error": "Server misconfiguration"}), 500

        # Define API details
        local_resource_id = "car_parks"  
        API_URL = "https://data.corkcity.ie/en_GB/api/3/action/datastore_search_sql"
        RESOURCE_ID = "f4677dac-bb30-412e-95a8-d3c22134e3c0"

        # Ensure API_URL is correctly formatted
        if not API_URL.startswith("https://"):
            logging.error("❌ Invalid API URL format.")
            return jsonify({"error": "API configuration error"}), 500

        # Fetch live parking data safely
        params = {"sql": f"SELECT * FROM {local_resource_id}"}  
        try:
            response = requests.get(API_URL, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ API request failed: {e}")
            return jsonify({"error": "Failed to retrieve live parking data"}), 500

        # Validate JSON response before accessing
        try:
            live_data = response.json().get("result", {}).get("records", [])
        except requests.exceptions.JSONDecodeError:
            logging.error("❌ API returned invalid JSON format.")
            return jsonify({"error": "Invalid JSON received from API"}), 500

        logging.debug(f"✅ Successfully retrieved {len(live_data)} live parking records.")

        # Fetch additional car park details from MySQL
        car_parks = car_parks_dao.get_all_car_parks()
        opening_hours = opening_hours_dao.get_all_opening_hours()

        logging.debug(f"✅ Fetched {len(car_parks)} stored car parks from database.")

        # Merge live spaces & opening hours into car parks
        for car_park in car_parks:
            car_park["live_spaces"] = next(
                (data for data in live_data if data.get("id") == car_park.get("id")), {}
            )
            car_park["opening_hours"] = next(
                (hours for hours in opening_hours if hours.get("car_park_id") == car_park.get("id")), {}
            )

        logging.debug("✅ Successfully merged parking data.")

        return jsonify(car_parks), 200

    except Exception as e:
        logging.error(f"❌ Unexpected error in fetch_parking_availability: {e}")
        return jsonify({"error": str(e)}), 500

# CRUD operations for Car Parks
# Fetch all car parks
# curl -X GET http://

@app.route('/api/car-parks', methods=['GET'])
def fetch_all_car_parks():
    logging.debug("Fetching car parks from MySQL...")
    
    car_parks = car_parks_dao.get_all_car_parks()  # DB stored parks
    live_spaces_data = live_spaces_dao.fetch_live_spaces()  # API fetched spaces

    # Merge live spaces into car park details
    for car_park in car_parks:
        car_park["live_spaces"] = next(
            (data for data in live_spaces_data if data["id"] == car_park["id"]), {}
        )

    return jsonify(car_parks), 200


# Create a new car park
# curl -X POST -H "Content-Type: application/json" -d '{"name": "Test Car
# Park", "height": 2.5}' http://127.0.0.1:5000/api/car-parks

@app.route('/api/car-parks', methods=['POST'])
def create_car_park():
    try:
        data = request.json
        schema = CarParkSchema()
        validated_data = schema.load(data)

        name = validated_data.get("name")
        height = validated_data.get("height")
        opening_hours = validated_data.get("opening_hours")

        car_park_id = car_parks_dao.create_car_park(name, height)
        for hours in opening_hours:
            opening_hours_dao.add_opening_hours(
                car_park_id, hours["day"], hours["opening_time"], hours["closing_time"], hours.get(
                    "status")
            )
        return jsonify({"message": "Car park created successfully"}), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        logging.error(f"Error creating car park: {e}")
        return jsonify({"error": str(e)}), 5000

# Update a car park
# curl -X PUT -H "Content-Type: application/json" -d '{"name": "Updated
# Car Park", "height": 3.0}' http://127.0.0.1:5000/api/car-parks/1

@app.route('/api/car-parks/<int:car_park_id>', methods=['PUT'])
def update_car_park(car_park_id):
    """
    Updates an existing car park with new details.

    Args:
        car_park_id (int): The ID of the car park to update.

    Returns:
        JSON response: Success or failure message.
    """
    try:
        data = request.json
        schema = CarParkSchema()
        validated_data = schema.load(data)

        # Extract data
        name = validated_data.get("name")
        height = validated_data.get("height")
        opening_hours = validated_data.get("opening_hours")

        # Check if car park exists before updating
        existing_car_park = car_parks_dao.get_car_park_by_id(car_park_id)
        if not existing_car_park:
            return jsonify({"error": "Car park not found"}), 404

        # Update car park details
        result = car_parks_dao.update_car_park(car_park_id, name, height)

        # Update opening hours
        for hours in opening_hours:
            opening_hours_dao.update_opening_hours(
                car_park_id, hours["day"], hours["opening_time"], hours["closing_time"], hours.get("status")
            )

        if result:
            return jsonify({"message": "Car park updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update car park"}), 500

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        logging.error("Error updating car park: %s", e)
        return jsonify({"error": str(e)}), 500

# Delete a car park
# curl -X DELETE http://127.0.0.1:5000/api/car-parks/1

@app.route('/api/car-parks/<int:car_park_id>', methods=['DELETE'])
def delete_car_park(car_park_id):
    try:
        result = car_parks_dao.delete_car_park(car_park_id)
        if result:
            return jsonify({"message": "Car park deleted successfully"}), 200
        else:
            return jsonify({"error": "Car park not found"}), 404
    except Exception as e:
        logging.error(f"Error deleting car park: {e}")
        return jsonify({"error": str(e)}), 500

# CRUD operations for Opening Hours
# Fetch opening hours for a specific car park

@app.route('/api/opening-hours/<int:car_park_id>', methods=['GET'])
def fetch_opening_hours(car_park_id):
    try:
        opening_hours = opening_hours_dao.get_opening_hours_for_car_park(
            car_park_id)
        return jsonify(opening_hours), 200
    except Exception as e:
        logging.error(f"Error fetching opening hours: {e}")
        return jsonify({"error": str(e)}), 500

# Add opening hours for a car park
# curl -X POST -H "Content-Type: application/json" -d '{"car_park_id": 1,
# "day": "Monday", "opening_time": "06:00", "closing_time": "20:00",
# "status": ""}' http://127.0.0.1:5000/api/opening-hours

@app.route('/api/opening-hours', methods=['POST'])
def add_opening_hours():
    try:
        data = request.json
        car_park_id = data.get("car_park_id")
        day = data.get("day")
        opening_time = data.get("opening_time")
        closing_time = data.get("closing_time")
        status = data.get("status")

        # Validate input
        if not car_park_id or not day or not (
                opening_time or closing_time or status):
            return jsonify({"error": "All fields are required"}), 400

        result = opening_hours_dao.add_opening_hours(
            car_park_id, day, opening_time, closing_time, status)
        if result:
            return jsonify(
                {"message": "Opening hours added successfully"}), 201
        else:
            return jsonify({"error": "Failed to add opening hours"}), 500
    except Exception as e:
        logging.error(f"Error adding opening hours: {e}")
        return jsonify({"error": str(e)}), 500

# Update opening hours for a car park
# curl -X PUT -H "Content-Type: application/json" -d '{"day": "Monday",
# "opening_time": "07:00", "closing_time": "21:00", "status": ""}'
# http://127.0.0.1:5000/api/opening-hours/1

@app.route('/api/opening-hours/<int:opening_hours_id>', methods=['PUT'])
def update_opening_hours(opening_hours_id):
    try:
        # Load and validate incoming data
        data = request.json
        schema = OpeningHoursSchema()
        validated_data = schema.load(data)

        # Extract data
        day = validated_data["day"]
        opening_time = validated_data["opening_time"]
        closing_time = validated_data["closing_time"]
        status = validated_data.get("status")

        # Update in database
        result = opening_hours_dao.update_opening_hours(
            opening_hours_id, day, opening_time, closing_time, status
        )
        if result:
            return jsonify(
                {"message": "Opening hours updated successfully"}), 200
        else:
            return jsonify({"error": "Opening hours not found"}), 404

    except ValidationError as err:
        # Return validation errors
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        logging.error(f"Error updating opening hours: {e}")
        return jsonify({"error": str(e)}), 500

# Delete opening hours for a car park
# curl -X DELETE http://127.0.0.1:5000/api/opening-hours/1

@app.route('/api/opening-hours/<int:opening_hours_id>', methods=['DELETE'])
def delete_opening_hours(opening_hours_id):
    try:
        result = opening_hours_dao.delete_opening_hours(opening_hours_id)
        if result:
            return jsonify(
                {"message": "Opening hours deleted successfully"}), 200
        else:
            return jsonify({"error": "Opening hours not found"}), 404
    except Exception as e:
        logging.error(f"Error deleting opening hours: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Registered Routes:", app.url_map)
    logging.debug("Starting the Flask server...")
    app.run(debug=True)