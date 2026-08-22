from flask import Flask, render_template, request
import mysql.connector
import os
import time

app = Flask(__name__)


def get_db_connection():

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "python-registration-mysql"),
        port=3306,
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "apppassword"),
        database=os.getenv("DB_NAME", "registration")
    )

    return connection


def initialize_database():

    while True:

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    course_name VARCHAR(100) NOT NULL,
                    country VARCHAR(100) NOT NULL
                )
            """)

            connection.commit()

            cursor.close()
            connection.close()

            print("Database initialized successfully.")

            break

        except mysql.connector.Error as error:

            print("MySQL not ready:", error)

            print("Retrying in 5 seconds...")

            time.sleep(5)


@app.route("/", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        username = request.form["username"]

        course_name = request.form["course_name"]

        country = request.form["country"]

        connection = get_db_connection()

        cursor = connection.cursor()

        sql = """
            INSERT INTO users
            (username, course_name, country)
            VALUES (%s, %s, %s)
        """

        values = (
            username,
            course_name,
            country
        )

        cursor.execute(sql, values)

        connection.commit()

        cursor.close()

        connection.close()

        message = "User registered successfully!"


    return render_template(
        "index.html",
        message=message
    )


if __name__ == "__main__":

    initialize_database()

    app.run(
        host="0.0.0.0",
        port=5000
    )
ubuntu@ip-172-31-39-112:~/Python-registration$ cat requirements.txt
Flask==3.1.0
mysql-connector-python==9.0.0
