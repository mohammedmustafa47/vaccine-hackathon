import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="1234",
    database="auth_db",
    port=3306
)

print("✅ Connected to MySQL successfully!")
conn.close()