from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DB_NAME = "library.db"


def get_db_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@app.route("/")
def home():
    return jsonify({
        "message": "Library API is running"
    })


@app.route("/loans", methods=["POST"])
def create_loan():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    required_fields = [
        "book_id",
        "reader_name",
        "loan_date"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    book_id = data["book_id"]
    reader_name = data["reader_name"]
    loan_date = data["loan_date"]

    connection = get_db_connection()

    # Проверяем, существует ли книга
    cursor = connection.execute(
        """
        SELECT id
        FROM books
        WHERE id = ?
        """,
        (book_id,)
    )

    book = cursor.fetchone()

    if book is None:
        connection.close()

        return jsonify({
            "error": "Book not found"
        }), 400

    # Проверяем, не выдана ли книга
    cursor = connection.execute(
        """
        SELECT id
        FROM loans
        WHERE book_id = ?
        AND returned = 0
        """,
        (book_id,)
    )

    active_loan = cursor.fetchone()

    if active_loan is not None:
        connection.close()

        return jsonify({
            "error": "Book is already on loan"
        }), 400

    # Создаём выдачу
    cursor = connection.execute(
        """
        INSERT INTO loans
        (book_id, reader_name, loan_date)
        VALUES (?, ?, ?)
        """,
        (book_id, reader_name, loan_date)
    )

    connection.commit()

    loan_id = cursor.lastrowid

    # Получаем созданную запись
    cursor = connection.execute(
        """
        SELECT
            id,
            book_id,
            reader_name,
            loan_date,
            returned
        FROM loans
        WHERE id = ?
        """,
        (loan_id,)
    )

    loan = cursor.fetchone()

    connection.close()

    return jsonify({
        "id": loan["id"],
        "book_id": loan["book_id"],
        "reader_name": loan["reader_name"],
        "loan_date": loan["loan_date"],
        "returned": loan["returned"]
    }), 201

@app.route("/loans/<int:loan_id>/return", methods=["PATCH"])
def return_loan(loan_id):
    connection = get_db_connection()

    # Ищем выдачу
    cursor = connection.execute(
        """
        SELECT
            id,
            book_id,
            reader_name,
            loan_date,
            returned
        FROM loans
        WHERE id = ?
        """,
        (loan_id,)
    )

    loan = cursor.fetchone()

    # Выдача не найдена
    if loan is None:
        connection.close()

        return jsonify({
            "error": "Loan not found"
        }), 404

    # Уже возвращена
    if loan["returned"] == 1:
        connection.close()

        return jsonify({
            "error": "Already returned"
        }), 400

    # Отмечаем как возвращённую
    connection.execute(
        """
        UPDATE loans
        SET returned = 1
        WHERE id = ?
        """,
        (loan_id,)
    )

    connection.commit()

    # Получаем обновлённую запись
    cursor = connection.execute(
        """
        SELECT
            id,
            book_id,
            reader_name,
            loan_date,
            returned
        FROM loans
        WHERE id = ?
        """,
        (loan_id,)
    )

    updated_loan = cursor.fetchone()

    connection.close()

    return jsonify({
        "id": updated_loan["id"],
        "book_id": updated_loan["book_id"],
        "reader_name": updated_loan["reader_name"],
        "loan_date": updated_loan["loan_date"],
        "returned": updated_loan["returned"]
    })

@app.route("/loans/active", methods=["GET"])
def get_active_loans():
    connection = get_db_connection()

    cursor = connection.execute("""
        SELECT
            loans.id AS loan_id,
            loans.reader_name AS reader_name,
            loans.loan_date AS loan_date,
            books.id AS book_id,
            books.title AS book_title,
            authors.name AS author_name
        FROM loans
        JOIN books
            ON loans.book_id = books.id
        JOIN authors
            ON books.author_id = authors.id
        WHERE loans.returned = 0
    """)

    rows = cursor.fetchall()

    connection.close()

    loans = []

    for row in rows:
        loans.append({
            "id": row["loan_id"],
            "reader_name": row["reader_name"],
            "loan_date": row["loan_date"],
            "book": {
                "id": row["book_id"],
                "title": row["book_title"],
                "author_name": row["author_name"]
            }
        })

    return jsonify(loans)


if __name__ == "__main__":
    app.run(debug=True)
