from gc import collect
from pydoc import resolve
from urllib import response
from flask import Flask, jsonify, abort, request
import pymongo
from pymongo import MongoClient, mongo_client
from dotenv import load_dotenv
import os
import auth_helper
import requests


app = Flask(__name__)
load_dotenv(".env")
cluster = MongoClient(os.environ.get("MONGO_URI"))
db = cluster["bookhub"]


@app.route('/')
def hello_geek():
    return '<h1>Hello We Are BookHub</h2>'

@app.route('/owns/<int:location_id>/<int:book_id>')
def getOwn(location_id, book_id):
    try:
        collection = db["owns"]
        response = jsonify({
            "owns": collection.find_one({
                "book_id":  book_id,
                "location_id": location_id
            }) 
        })
        response.status_code = 200
        return response
    except:
        abort(404)

@app.route('/locations')
def getLocation():
    try:
        collection = db["location"]
        response = jsonify(list(collection.find({})))
        response.status_code = 200

        return response
    except:
        abort(404)

@app.route('/locations/<int:location_id>')
def getOneLocation(location_id):
    try:
        collection = db["location"]
        response = jsonify({
            "location": collection.find_one({"_id": location_id})
            })
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
        response = jsonify({
            "data": list(collection.find({}))
            })
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
        response = jsonify({
            "data" : list(collection.find({
            "$text": {"$search": text_search}
        }))})
        response.status_code = 200

        return response
    except:
        abort(404)


# AUTHENTICATE
@app.route("/auth_exchange", methods=["POST"])
def auth_exchange_handler():
    data_dict = request.get_json()

    if not data_dict:
        msg = "No payload received"
        return f"Bad Request: {msg}", 400

    if not isinstance(data_dict, dict):
        msg = "Invalid payload data format"
        return f"Bad Request: {msg}", 400

    if not "code" in data_dict:
        msg = "Missing key 'code'"
        return f"Bad Request: {msg}", 400

    try:
        output = auth_helper.new_request_auth_exchange(data_dict)
        return output, 200
    except Exception as err:
        return f"Error: {err}", 500


@app.route("/auth_refresh", methods=["POST"])
def auth_refresh():
    data_dict = request.get_json()

    if not data_dict:
        msg = "No payload received"
        return f"Bad Request: {msg}", 400

    if not isinstance(data_dict, dict):
        msg = "Invalid payload data format"
        return f"Bad Request: {msg}", 400

    if not "refresh_token" in data_dict:
        msg = "Missing key 'refresh_token'"
        return f"Bad Request: {msg}", 400

    try:
        output = auth_helper.refresh_token(data_dict)
        return output, 200
    except Exception as err:
        return f"Error: {err}", 500


@app.route("/auth_info", methods=["POST"])
def auth_info():
    data_dict = request.get_json()

    if not data_dict:
        msg = "No payload received"
        return f"Bad Request: {msg}", 400

    if not isinstance(data_dict, dict):
        msg = "Invalid payload data format"
        return f"Bad Request: {msg}", 400

    if not "access_token" in data_dict:
        msg = "Missing key 'access_token'"
        return f"Bad Request: {msg}", 400

    try:
        output = auth_helper.get_info(data_dict)
        return output, 200
    except Exception as err:
        return f"Error: {err}", 500

#--------------------------------------------------------


# @app.route("/cart", method=["POST"])
# def addToCart(cart):
#     data = request.get_json()
#     authCode = data["authCode"]
#     try:
#         # VERIFY USER
#         res = auth_helper.get_info(
#             jsonify({
#                 "access_token":authCode}))
#         if res.status_code != 200:

#     except:
#         abort(404)






@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Resource not found',
        'status': 404
    })
    response.status_code = 404
    return response


if __name__ == "__main__":
    app.run(debug=True)
