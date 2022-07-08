from pydoc import resolve
from flask import Flask, jsonify, abort, request
import pymongo
from pymongo import MongoClient, mongo_client
import os


app = Flask(__name__)
cluster = MongoClient("mongodb+srv://khangkontum:anhyeuem123@bookhub.gl5cb.mongodb.net/?retryWrites=true&w=majority")
db = cluster["bookhub"]


@app.route('/')
def hello_geek():
    return '<h1>Hello We Are BookHub</h2>'


@app.route('/locations')
def getLocation():
    try:
        collection = db["location"]
        response = jsonify(list(collection.find({})))
        response.status_code = 200

        return response
    except:
        abort(404)


@app.route('/books/<int:book_id>')
def getOneBook(book_id):
    try:
        book_collection = db["book"]
        owns_collection = db["owns"]
        response = jsonify({
            "book": book_collection.find_one({"_id": book_id}),
            "location": list(owns_collection.find({"book_id": book_id}))
        })

        response.status_code = 200
        return response
    except:
        abort(404)


@app.route('/books', methods=['GET'])
def getBooks():
    try:
        collection = db["book"]
        response = jsonify(list(collection.find({})))
        response.status_code = 200

        return response
    except:
        abort(404)


@app.route('/books/search', methods=['GET'])
def searchBook():
    try:
        args = request.args
        text_search = args.get('q')
        print(text_search)

        collection = db["book"]
        response = jsonify(list(collection.find({
            "$text": {"$search": text_search}
        })))
        response.status_code = 200

        return response
    except:
        abort(404)


@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Resource not found',
        'status': 404
    })
    response.status_code = 404
    return response


if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(debug=True, port=port)
