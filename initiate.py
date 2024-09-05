import mysql.connector
from faker import Faker
from random import choice, randint

# Establish connection to the MySQL server
def create_connection(host_name, user_name, user_password, db_name=None):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name  # Specify the database during connection
        )
        print("Connection to MySQL DB successful")
    except mysql.connector.Error as e:
        print(f"The Exception '{e}' occurred")
    return connection

# Execute a query
def execute_query(connection, query,data=None):
    if connection is None:  # Check if connection is valid
        print("No valid connection. Cannot execute query.")
        return None
    cursor = connection.cursor()
    try:
      if data:
        cursor.executemany(query,data)
      else:
        cursor.execute(query)
      if cursor.with_rows:  # Check if the query has a result set
          result = cursor.fetchall()
          # print("Query executed successfully and result fetched.")
          return result
      connection.commit()
      # print("Query executed successfully (no result set).")
    except Exception as e:
        print(f"While executing {query[:50]}")
        print(f"The Exception '{e}' occurred")
        return None
    finally:
        cursor.close()  # Ensure the cursor is closed after use
    return None
  
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


# Connect to MySQL server
connection = create_connection("127.0.0.1", "root", "password", "hospital_db")

if __name__ == '__main__':


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
  create table if not exists Meditag Meditag(
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