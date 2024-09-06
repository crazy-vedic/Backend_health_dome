from flask import Flask, jsonify, request,send_from_directory
from initiate import retrieve_connection, execute_query, insert_random_data
from flask_swagger_ui import get_swaggerui_blueprint



app = Flask(__name__)

swaggerui_blueprint = get_swaggerui_blueprint(
    '/apidocs',
    '/static/swagger.yaml',
    config={  # Swagger UI configuration options
        'app_name': "Simple Bed Manager API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix='/apidocs')



@app.route('/', methods=['GET'])
def home():
    """
    Home route that provides Swagger documentation.
    ---
    get:
      summary: Provides Swagger documentation
      description: |
        Returns the Swagger UI for the API documentation.
      responses:
        '200':
          description: Swagger UI
    """
    return send_from_directory('static', 'index.html')
    
@app.route('/insert-random-data', methods=['GET'])
def insert_data():
    # Insert random data
    with retrieve_connection() as connection:
        if connection is None:
            return jsonify({"error": "Unable to establish connection to the database."}), 500
    insert_random_data(connection, insert_patients=True, insert_beds=True, insert_history=True, insert_medicines=True, insert_meditags=True)

    return jsonify({"status": "Random data inserted successfully!"})


@app.route('/beds', methods=['GET'])
def get_beds():
    """
    Retrieve bed information based on query parameters.
    """
    filters = request.args.to_dict()  # Converts all query parameters to a dictionary
    base_query = 'SELECT * FROM Bed'
    conditions = []
    values = []
    for column, value in filters.items():
        conditions.append(f"{column} = %s")
        values.append(value)

    # Add conditions to the base query if there are any filters
    if conditions:
        base_query += ' WHERE ' + ' AND '.join(conditions)

    with retrieve_connection() as connection:
        if connection is None:
            return jsonify({"error": "Unable to establish connection to the database."}), 500
        result = execute_query(connection, base_query, values if len(values) > 0 else None)
    return jsonify(result)

@app.route('/set_bed', methods=['POST'])
def set_bed():
    """
    Update the status and/or Pid of a bed given its BedID.
    """
    data = request.json  # Parse the incoming JSON data

    # Validate that 'bedID' is provided and at least one of 'status' or 'Pid' is present
    if not data or not data.get('bedID') or ('status' not in data and 'Pid' not in data):
        return jsonify({"error": "Missing 'bedID' or both 'status' and 'Pid' are missing in the request."}), 400

    # Dynamically build the SQL query based on provided data
    update_fields = []
    values = []

    if 'status' in data:
        update_fields.append("Status = %s")
        values.append(data['status'])
    
    if 'Pid' in data:
        update_fields.append("Pid = %s")
        values.append(data['Pid'])
    # Ensure we have fields to update
    if not update_fields:
        return jsonify({"error": "No valid fields to update."}), 400

    values.append(data['bedID'])  # Add 'bedID' as the last parameter

    # Construct the dynamic SQL query
    query = f"UPDATE Bed SET {', '.join(update_fields)} WHERE BedID = %s;"

    try:
        with retrieve_connection() as connection:
            if connection is None:
                return jsonify({"error": "Unable to establish connection to the database."}), 500
            result = execute_query(connection, query, values)
        return jsonify(result) if result else jsonify({"message": "Update successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return HTTP 500 for internal server error


if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)