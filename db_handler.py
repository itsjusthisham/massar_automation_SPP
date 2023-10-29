import sqlite3

conn = sqlite3.connect('./db/login.db')

cursor = conn.cursor()

# create_table_query = '''
#     CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY,
#         email TEXT,
#         password TEXT
#     )
# '''
# cursor.execute(create_table_query)

# insert_query = '''
#     INSERT INTO users (email, password)
#     VALUES (?, ?)
# '''
# user_data = ('EZZAMZAMI.HICHAM@taalim.ma', 'EZHI@2023')
# cursor.execute(insert_query, user_data)

# select_query = '''
#     SELECT * FROM users
# '''
# cursor.execute(select_query)
# result = cursor.fetchall()
# for row in result:
#     print(row)

delete_query = "DELETE FROM users"

# Assuming 'id' is the primary key column
row_id = 1  # Replace with the specific row ID you want to delete

cursor.execute(delete_query)

conn.commit()
conn.close()

# // "start": "electron-forge start",