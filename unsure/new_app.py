from flask import Flask
import mysql.connector

app = Flask(__name__)

# Database Configuration (Replace with your actual details)
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "carparks",
    "port": 3306
}

@app.route("/test-db")
def test_db():
    try:
        connection = mysql.connector.connect(**db_config)
        return "✅ Connected to MySQL!"
    except mysql.connector.Error as e:
        return f"❌ Connection failed: {e}"
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    app.run(debug=True)
