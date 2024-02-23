from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins


@app.route("/get_btn_state")
def get_btn_state():
    print("002")
    try:
        with sql.connect('shot_database.db') as con:
            c = con.cursor()
            c.execute("SELECT carState FROM CarStates ORDER BY id DESC LIMIT 1")
            row = c.fetchone()

            if row:
                car_state = row[0]
                print("003")
                return jsonify({"carState": car_state})
                
            else:
                print("004")
                return jsonify({"message": "No button state recorded yet."}), 204

    except sql.Error as e:
        print("005")
        print(f"Error retrieving button state: {e}")
        return jsonify({"error": "Failed to retrieve button state"}), 500



@app.route("/home")
def home():
    # Get the last button state and pass it to the template
    print("001")
    last_state = get_btn_state()
    print("006")
    print(f" the car is: {last_state}")
    if last_state.is_json:
        # Assuming successful retrieval
        car_state = last_state.get_json()["carState"]
        print(f" the car is: {car_state}")
    else:
        # Handle error or no state found
        car_state = "off"  # Or a default value

    return render_template("index.html", car_state=car_state)

@app.route("/data", methods=["POST"])
def receive_data():

    # data = request.json  # Access JSON data sent from ESP32
    # # Process and store the data
    # # Optionally, send a response back
    # print(data)


    data = request.json
    sensor1_value = data.get("sensor1")
    sensor2_value = data.get("sensor2")

    # # Process and store the data
    print(f"sensor 1: {sensor1_value} \nsensor 2: {sensor2_value}")

    try:
        # Connect to database (using context manager)
        with sql.connect('shot_database.db') as con:
            c = con.cursor()

            # Create table if it doesn't exist
            c.execute("""CREATE TABLE IF NOT EXISTS Shots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor1 REAL,
                sensor2 REAL
            )""")

            # Insert data with correct data types
            c.execute("INSERT INTO Shots (sensor1, sensor2) VALUES (?, ?)", (sensor1_value, sensor2_value))
            # Commit changes
            con.commit()
        return jsonify({"message": "Data saved successfully!"}), 201
        

    except sql.Error as e:
        print(f"Error saving data: {e}")
        
        return jsonify({"error": "Failed to save data"}), 500

    # Close connection and cursor (handled by context manager)

@app.route("/btn_data", methods=["POST"])
def receive_btn_data():
    data = request.json
    car_state = data.get("carState")

    # Process and store the data
    print(f"Car state: {car_state}")

    try:
        with sql.connect('shot_database.db') as con:
            c = con.cursor()

            # Create table if it doesn't exist
            c.execute("""CREATE TABLE IF NOT EXISTS CarStates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                carState TEXT
            )""")

            # Insert data with correct data types
            c.execute("INSERT INTO CarStates (carState) VALUES (?)", (car_state,))
            con.commit()
        return jsonify({"message": "Button data saved successfully!"}), 201

    except sql.Error as e:
        print(f"Error saving button data: {e}")
        return jsonify({"error": "Failed to save button data"}), 500



@app.route("/get_data", methods=["GET"])
def get_data():
    try:
        # Connect to database (using context manager)
        with sql.connect('shot_database.db') as con:
            c = con.cursor()

            # Execute query to retrieve data
            c.execute("SELECT * FROM Shots")

            # Fetch all results as a list of tuples
            data = c.fetchall()

        # Build response with retrieved data
        return jsonify({"data": data}), 200

    except sql.Error as e:
        print(f"Error retrieving data: {e}")
        return jsonify({"error": "Failed to retrieve data"}), 500


if __name__ == "__main__":
    app.run(debug=True)
