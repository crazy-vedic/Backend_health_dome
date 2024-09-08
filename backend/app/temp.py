from flask import Flask, jsonify, request, send_from_directory
from initiate import retrieve_connection, execute_query, insert_random_data
import logging
from flask_cors import CORS
from os import getenv

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins


@app.route('/beds', methods=['GET'])
def get_beds():
    """
    Retrieve bed information based on query parameters.
    """
    
    result = [(1,'General','stupid','Available'),(2,'ICU','shit','Occupied')]
    return jsonify(result)


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True,port=5001)
