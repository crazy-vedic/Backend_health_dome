from initiate import connection, execute_query

# Execute query to show tables
result = execute_query(connection, 'SHOW TABLES;')

for table in result:
    table=table[0]
    print(table,'\n','\n'.join(list(map(str,execute_query(connection, f"DESCRIBE {table};")))))