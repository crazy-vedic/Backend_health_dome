from initiate import retrieve_connection, execute_query

connection = retrieve_connection()
# Execute query to show tables
result = execute_query(connection, 'SHOW TABLES;')

for table in result:
    table=table[0]
    print(table,'\n','\n'.join(list(map(str,execute_query(connection, f"DESCRIBE {table};")))))