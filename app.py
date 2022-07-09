from gc import collect
from json import JSONDecoder
import json
from pydoc import resolve
from urllib import response
from flask import Flask, jsonify, abort, request
from helper_func import decodeResponse, parse_json
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
@app.route("/cart", methods=["POST", "DELETE", "GET"])
def addToCart():

    body = request.get_json()
    if not "access_token" in body:
        abort(400)

    access_token = body["access_token"]
    data = auth_helper.auth_code({"access_token":access_token})
    data = decodeResponse(data)

    if request.method == 'GET':
        try:
            customer_id = data["data"]["customer_id"]
            collection = db["cart"]
            data = collection.find_one({"_id": customer_id})
            response = jsonify( { "cart":  collection.find_one({"_id": customer_id}) })
            response.status_code = 200
            return response
        except:
            abort(404)

    if request.method == 'POST':
        try:
            if (not "from" in body) or (not "to" in body) or (not "book_id" in body) or (not "location_id" in body):
                abort(400)
            customer_id = data["data"]["customer_id"]

            collection = db["cart"]
            currentCart = collection.find_one({
                "customer_id": customer_id
            })
            if(currentCart == None):
                currentCart = collection.insert_one({
                    "_id": customer_id,
                    "customer_id": customer_id,
                    "book_list": []})

            collection.update_one(
                {"customer_id": customer_id,},
                {"$push": {"book_list": {
                    "book_id": body["book_id"],
                    "from": body["from"],
                    "to": body["to"],
                    "location_id": body["location_id"]
                    }}}
            )
            response = jsonify({
                "cart": collection.find_one({
                "customer_id": customer_id})
            }) 
            response.status_code = 200
            return response
        except:
            abort(404)
    if request.method == 'DELETE':
        try:
            customer_id = data["data"]["customer_id"]

            collection = db["cart"]
            currentCart = collection.find_one({
                "customer_id": customer_id
            })
            if(currentCart == None):
                currentCart = collection.insert_one({
                    "_id": customer_id,
                    "customer_id": customer_id,
                    "book_list": []})

            collection.update_one(
                {"customer_id": customer_id,},
                {"$pull": {"book_list": body["book_id"]}}
            )
            response = jsonify({
                "cart": collection.find_one({
                "customer_id": customer_id})
            }) 
            response.status_code = 200
            return response
        except:
            abort(404)


@app.route("/cart/confirm", methods=["POST"])
def confirmCart():
    body = request.get_json()
    if not "access_token" in body:
        abort(400)

    access_token = body["access_token"]
    data = auth_helper.auth_code({"access_token":access_token})
    data = decodeResponse(data)
    try:
        customer_id = data["data"]["customer_id"]
        cartCollection = db['cart']
        historyCollection = db['history']

        currentCart = cartCollection.find_one({"_id": customer_id})
        if (currentCart == None):
            abort(404)
        for product in currentCart["book_list"]:
            historyCollection.insert_one({
                "customer_id": customer_id,
                "book": product
                })
        response = jsonify({
            "data": "ok" })
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
        abort(404)


@app.route("/history", methods=["GET"])
def getHistory():
    if request.method == "GET":
        try:
            body = request.get_json()
            if not "access_token" in body:
                msg = "Missing key 'access_token'"
                return f"Bad Request: {msg}", 400

            access_token = body["access_token"]
            data = auth_helper.auth_code({"access_token":access_token})
            data = decodeResponse(data)

            customer_id = data["data"]["customer_id"]

            collection = db["history"]
            response = parse_json({
                "history": list(collection.find({
                    "customer_id": customer_id}))})
            response['status_code'] = 200
            return response
        except Exception as e:
            print(e)
            abort(404)











@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Resource not found',
        'status': 404
    })
    response.status_code = 404
    return response

@app.errorhandler(400)
def not_found(error=None):
    msg = "Missing key 'access_token'"
    return f"Bad Request: {msg}", 400


if __name__ == "__main__":
    app.run(debug=True)
