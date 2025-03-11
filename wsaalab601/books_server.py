from flask import Flask, url_for, request, redirect, jsonify, abort

app = Flask(__name__, static_url_path="", static_folder="staticpages")

# Sample data: a collection of books
books = [
    {"id": 1, "title": "1984", "author": "George Orwell"},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee"},
    {"id": 3, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    {"id": 4, "title": "One Hundred Years of Solitude", "author": "Gabriel Garcia Marquez"},
]

# Test to see it works
@app.route('/')
def index():
    return 'It works!'

# Route to get all books
# curl http://127.0.0.1:5000/books
@app.route("/books", methods=["GET"])
def get_books():
    return jsonify({"books": books})

# Route to get a specific book by ID
# curl http://127.0.0.1:5000/books/3
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((book for book in books if book["id"] == book_id), None)
    return jsonify({"book": book}) if book else ("Book not found", 404)

# Route to add a new book
@app.route("/books", methods=["POST"])
def add_book():
    new_book = request.get_json()
    books.append(new_book)
    return jsonify(new_book), 201

# Route to update a book by ID
# curl -X PUT -d "{\"title\":\"test\", \"author\":\"some guy\", \"price\":123}" http://127.0.0.1:5000/books/1
# curl -X PUT -H "Content-Type: application/json" -d '{"title":"test", "author":"some guy", "price":123}' http://127.0.0.1:5000/books/1 (From Co-pilot)
# curl -X PUT -H "Content-Type: application/json" -d "{\"title\":\"test\", \"author\":\"some guy\", \"price\":123}" http://127.0.0.1:5000/books/1 (in VS Code)


@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = next((book for book in books if book["id"] == book_id), None)
    if book:
        updated_data = request.get_json()
        book.update(updated_data)
        return jsonify(book)
    else:
        return ("Book not found", 404)

# Route to delete a book by ID
# curl -X DELETE  http://127.0.0.1:5000/books/1
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    global books
    books = [book for book in books if book["id"] != book_id]
    return ("Book deleted", 204)

if __name__ == "__main__":
    app.run(debug=True)
