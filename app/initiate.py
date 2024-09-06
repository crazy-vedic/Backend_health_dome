import mysql.connector
from faker import Faker
from random import choice, randint
from os import getenv

# Establish connection to the MySQL server
def create_connection(host_name, user_name, user_password, db_name=None):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name
        )
        if connection.is_connected():
          print("Connection to MySQL DB successful")
          return connection
        else:
          raise mysql.connector.Error("Connection to MySQL DB failed")
    except mysql.connector.Error as e:
        print(f"The Exception '{e}' occurred")
        raise

# Execute a query
def execute_query(connection, query,data=None):
    if connection is None:  # Check if connection is valid
        print("No valid connection. Cannot execute query.")
        return None
    cursor = connection.cursor()
    try:
      if data is None:
        cursor.execute(query)
      elif isinstance(data[0],tuple):
        cursor.executemany(query,data)
      #elif data is not None:
      else:
        cursor.execute(query, data)
      if cursor.with_rows:  # Check if the query has a result set
          result = cursor.fetchall()
          # print("Query executed successfully and result fetched.")
          return result
      connection.commit()
      status_message = {
            "message": "Query OK",
            "rows_affected": cursor.rowcount,
            "rows_matched": cursor.rowcount,  # Rows matched would be the same as affected in most cases
            "warnings": [] if cursor.warning_count else cursor.warnings  # Fetch warnings, if any
        }

      # print("Query executed successfully (no result set).")
    except Exception as e:
        print(f"While executing {query[:50]}")
        print(f"The Exception '{e}' occurred")
        return None
    finally:
        cursor.close()  # Ensure the cursor is closed after use
    return status_message
  
def insert_random_data(connection, insert_patients=False, insert_beds=False, insert_history=False, insert_medicines=False, insert_meditags=False):
  fake=Faker()
  # Insert data into the 'Patient' table
  if insert_patients:
    insert_patient_query = '''
    INSERT INTO Patient (PatientID, Name, Phone, Age, Sex)
    VALUES (%s, %s, %s, %s, %s)
    '''
    patient_data = [(i, fake.name(), fake.phone_number()[:14], randint(1, 100), choice(['M', 'F'])) for i in range(1, 11)]
    print(patient_data)
    execute_query(connection, insert_patient_query, patient_data)
  
  # Insert data into the 'Bed' table
  if insert_beds:
    insert_bed_query = '''
    INSERT INTO Bed (Type, Location, Status, Pid)
    VALUES (%s, %s, %s, %s)
    '''
    status = [choice(['Available', 'Occupied', 'Reserved']) for _ in range(11)]
    bed_data = [(choice(['General', 'ICU', 'Private']), F"{choice(['A','B','C'])}/{randint(0,3)}{randint(10,99)}", status[i], randint(1, 9) if status[i]=='Occupied' else None) for i in range(0,11)]
    print('\n'.join(list(map(str,bed_data))))
    execute_query(connection, insert_bed_query, bed_data)

  # # Insert data into the 'History' table
  if insert_history:
    insert_history_query = '''
    INSERT INTO History (PID, Doctor, Date, PrescriptionID)
    VALUES (%s, %s, %s, %s)
    '''
    history_data = [(randint(1, 11), fake.name(), fake.date_between(start_date='-1y', end_date='today'), fake.uuid4()[:8]) for _ in range(10)]
    execute_query(connection, insert_history_query, history_data)
  
  # Insert data into the 'Medicine' table
  if insert_medicines:
    insert_medicine_query = '''
    INSERT INTO Medicine (MediName, Qty)
    VALUES (%s, %s)
    '''
    medicine_data = [(generate_medication_name(), randint(1, 100)) for _ in range(10)]
    execute_query(connection, insert_medicine_query, medicine_data)

  # Insert data into the 'Meditag' table
  if insert_meditags:
      insert_meditag_query = '''
      INSERT INTO Meditag (MediID, MediTag)
      VALUES (%s, %s)
      '''
      # Assume the Medicine IDs are from 1 to 10 for demonstration
      meditag_data = [(i, choice(['Painkiller', 'Antibiotic', 'Supplement', 'Antiseptic'])) for i in range(1,11)]
      execute_query(connection, insert_meditag_query, meditag_data)


def generate_medication_name():
    base_names = ["Aero", "Cura", "Helio", "Nova", "Vita", "Zeno", "Riva", "Lumen", "Medi", "Nex"]
    modifiers = ["Clear", "Max", "Prime", "Sure", "Ultra", "Gen", "Flex", "Opti", "Plus", "Pure"]
    suffixes = ["-in", "-ol", "-ex", "-am", "-an", "-ium", "-or", "-ide", "-ine", "-ar"]
    return f"{choice(base_names)}{choice(modifiers)}{choice(suffixes)}"


def retrieve_connection(
    host_name=getenv('MYSQL_HOST'),  # Use 'mysql' as hostname within Docker network
    user_name=getenv('MYSQL_USER'),
    user_password=getenv('MYSQL_PASSWORD'),
    db_name=getenv('MYSQL_DATABASE')
):
    connection = create_connection(host_name, user_name, user_password, db_name)
    return connection

if __name__ == '__main__':

  connection = retrieve_connection()
  insert_random_data(connection)
  # Create Database
  create_database_query = "CREATE DATABASE IF NOT EXISTS hospital_db"
  # Connect to the new database

  # Create Tables
  execute_query(connection, create_database_query)
  create_bed_table = """
  CREATE TABLE IF NOT EXISTS Bed (
    BedID INT AUTO_INCREMENT PRIMARY KEY,
    Type VARCHAR(50),
    Location VARCHAR(100),
    Status VARCHAR(50)
  );
  """
  create_medicine_table = """
  CREATE TABLE IF NOT EXISTS Medicine (
    MediID INT AUTO_INCREMENT PRIMARY KEY,
    MediName VARCHAR(100),
    Qty INT
  );
  """
  create_meditag_table='''
  create table if not exists Meditag(
MediID int,
MediTag varchar(50),
foreign key (MediID) references Medicine(MediID),
PRIMARY KEY (MediID,MediTag));
  '''
  create_patient_table = """
  CREATE TABLE IF NOT EXISTS Patient (
    PatientID INT PRIMARY KEY,
    Name VARCHAR(100),
    Phone VARCHAR(15),
    Age INT,
    Sex CHAR(1)
  );
  """
  create_history_table = """
  CREATE TABLE IF NOT EXISTS History (
    PID INT,
    Doctor VARCHAR(100),
    Date DATE,
    PrescriptionID VARCHAR(50),
    FOREIGN KEY (PID) REFERENCES Patient(PatientID),
    PRIMARY KEY (PID, Date, PrescriptionID)
  );
  """
  for query in [create_bed_table, create_medicine_table, create_patient_table, create_history_table,create_meditag_table]:
      execute_query(connection, query)
  connection.close()