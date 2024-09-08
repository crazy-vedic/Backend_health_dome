from flask import Flask, jsonify, request, send_from_directory
from initiate import retrieve_connection, execute_query, insert_random_data
from flask_swagger_ui import get_swaggerui_blueprint
import logging
from flask_cors import CORS
from os import getenv

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

swaggerui_blueprint = get_swaggerui_blueprint(
    '/apidocs',
    '/static/swagger.yaml',
    config={  # Swagger UI configuration options
        'app_name': "Simple Bed Manager API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix='/apidocs')


def parse_filters(filters):
    """
    Parse filter strings and return conditions and values for SQL queries.
    """
    base_query = ''
    conditions = []
    values = []

    for filter_str in filters:
        if '=' in filter_str:
            column, value = filter_str.split('=', 1)
            operator = '='
        elif '>' in filter_str:
            column, value = filter_str.split('>', 1)
            operator = '>'
        elif '<' in filter_str:
            column, value = filter_str.split('<', 1)
            operator = '<'
        else:
            continue  # skip invalid filters
        
        column = column.strip()
        value = value.strip()
        conditions.append(f"{column} {operator} %s")
        values.append(value)
    
    return conditions, values


@app.route('/details', methods=['GET'])
def get_details():
    return jsonify({"hospital_name":getenv('HOSPITAL_NAME','Vasant Kunj Hospital')})

@app.route('/', methods=['GET'])
def home():
    """
    Home route that provides Swagger documentation.
    """
    return send_from_directory('static', 'index.html')


@app.route('/insert-random-data', methods=['GET'])
def insert_data():
    try:
        with retrieve_connection() as connection:
            if connection is None:
                return jsonify({"error": "Unable to establish connection to the database."}), 500
            response = insert_random_data(connection, insert_patients=True, insert_beds=True, insert_history=True, insert_medicines=True, insert_meditags=True)
        return jsonify({"status": "Random data inserted successfully!", "response": response})
    except Exception as e:
        logging.error(f"Failed to insert random data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/patients', methods=['GET'])
def get_patients():
    """
    Retrieve patient information based on query parameters.
    """
    filters = request.args.get('filters', default='').split(',')
    base_query = 'SELECT * FROM Patient'
    conditions, values = parse_filters(filters)
    
    if conditions:
        base_query += ' WHERE ' + ' AND '.join(conditions)
    
    logging.info(f"Executing query: {base_query}")
    
    try:
        with retrieve_connection() as connection:
            if connection is None:
                return jsonify({"error": "Unable to establish connection to the database."}), 500
            result = execute_query(connection, base_query, values if values else None)
            return jsonify(result)
    except Exception as e:
        logging.error(f"Query failed: {e}")
        return jsonify({"message": "Query execution failed.", "error": str(e)}), 500


@app.route('/beds', methods=['GET'])
def get_beds():
    """
    Retrieve bed information based on query parameters.
    """
    filters = request.args.get('filters', default='').split(',')
    base_query = 'SELECT * FROM Bed'
    conditions, values = parse_filters(filters)

    if conditions:
        base_query += ' WHERE ' + ' AND '.join(conditions)
    
    logging.info(f"Executing query: {base_query}")
    
    try:
        with retrieve_connection() as connection:
            if connection is None:
                return jsonify({"error": "Unable to establish connection to the database."}), 500
            result = execute_query(connection, base_query, values if values else None)
            return jsonify(result)
    except Exception as e:
        logging.error(f"Query failed: {e}")
        return jsonify({"message": "Query execution failed.", "error": str(e)}), 500


@app.route('/set_bed', methods=['POST'])
def set_bed():
    """
    Update the status and/or Pid of a bed given its BedID.
    """
    data = request.json

    if not data or not data.get('bedID') or ('status' not in data and 'Pid' not in data):
        return jsonify({"error": "Missing 'bedID' or both 'status' and 'Pid' are missing in the request."}), 400

    update_fields = []
    values = []

    if 'status' in data:
        update_fields.append("Status = %s")
        values.append(data['status'])
    
    if 'Pid' in data:
        update_fields.append("Pid = %s")
        values.append(data['Pid'])

    if not update_fields:
        return jsonify({"error": "No valid fields to update."}), 400

    values.append(data['bedID'])

    query = f"UPDATE Bed SET {', '.join(update_fields)} WHERE BedID = %s;"

    try:
        with retrieve_connection() as connection:
            if connection is None:
                return jsonify({"error": "Unable to establish connection to the database."}), 500
            result = execute_query(connection, query, values)
        return jsonify(result) if result else jsonify({"message": "Update successful"}), 200
    except Exception as e:
        logging.error(f"Update failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/medicines', methods=['GET'])
def get_medicines():
    """
    Retrieve medicine information based on query parameters.
    """
    filters = request.args.get('filters', default='').split(',')
    base_query = 'SELECT * FROM Medicine'
    conditions, values = parse_filters(filters)

    if conditions:
        base_query += ' WHERE ' + ' AND '.join(conditions)
    
    logging.info(f"Executing query: {base_query}")
    
    try:
        with retrieve_connection() as connection:
            if connection is None:
                return jsonify({"error": "Unable to establish connection to the database."}), 500
            result = execute_query(connection, base_query, values if values else None)
            return jsonify(result)
    except Exception as e:
        logging.error(f"Query failed: {e}")
        return jsonify({"message": "Query execution failed.", "error": str(e)}), 500

@app.route('/set_medicine', methods=['POST'])
def set_medicine():
    """
    Update the quantity and/or expiry date of a medicine given its MediID.
    """
    data = request.json

    if not data or not data.get('MediID') or ('Qty' not in data and 'Expiry' not in data):
        return jsonify({"error": "Missing 'MediID' or both 'Qty' and 'Expiry' are missing in the request."}), 400

    update_fields = []
    values = []

    if 'Qty' in data:
        update_fields.append("Qty = %s")
        values.append(data['Qty'])
    
    if 'Expiry' in data:
        update_fields.append("Expiry = %s")
        values.append(data['Expiry'])

    if not update_fields:
        return jsonify({"error": "No valid fields to update."}), 400

    values.append(data['MediID'])

    query = f"UPDATE Medicine SET {', '.join(update_fields)} WHERE MediID = %s;"

    try:
        with retrieve_connection() as connection:
            if connection is None:
                return jsonify({"error": "Unable to establish connection to the database."}), 500
            result = execute_query(connection, query, values)
        return jsonify(result) if result else jsonify({"message": "Update successful"}), 200
    except Exception as e:
        logging.error(f"Update failed: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
