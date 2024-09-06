from flask import Flask, jsonify, request
from initiate import retrieve_connection, execute_query

app = Flask(__name__)


@app.route('/beds', methods=['GET'])
def get_beds():
    '''
    Dynamic filtering to access the beds information:
    GET /beds?Status=Occupied
    SELECT * FROM Bed WHERE Status = 'Occupied';
    GEt /beds?Status=Occupied&Type=Private
    SELECT * FROM Bed WHERE Status = 'Occupied' AND Type = 'Private' ;
    '''
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
        result = execute_query(connection, base_query, values if len(values) > 0 else None)
    return jsonify(result)

@app.route('/set_bed', methods=['POST'])
def set_bed():
    """
    Data must have the following format:
    {
        "status": "Occupied",  # Optional
        "Pid": 1               # Optional
        "bedID": 135,          # Required
    }
    Set the status and Pid of a bed, given its BedID
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
            result = execute_query(connection, query, values)
        return jsonify(result) if result else jsonify({"message": "Update successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return HTTP 500 for internal server error


if __name__ == '__main__':
    app.run(debug=True)