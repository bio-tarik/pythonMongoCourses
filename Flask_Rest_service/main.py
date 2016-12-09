from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.json_util import dumps, loads
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.onychophora


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


# default page
@app.route('/')
def default():
    return "Hello!"


# READ GET
# If no parameters are found, return as a JSON every item on the collection. Otherwise, returns matched items JSON
@app.route('/read/<collection>')
def read(collection):
    try:
        source = request.args if len(request.args) > 0 else request.form
        if len(source) == 0:
            _item = db[collection].find()
            return dumps(_item)
        else:
            _request = dumps(source)
            items = db[collection].find(loads(_request))
            return dumps(items)

    except Exception:
        raise


# READ_BY_ID GET
# Searches an item using its object id. Expects an _id parameter
# return found item as a JSON
@app.route('/read_by_id/<collection>')
def read_by_id(collection):
    try:
        source = request.args if len(request.args) > 0 else request.form
        if len(source) == 0:
            raise Exception("Invalid request")
        elif len(source['_id']) == 0:
            raise Exception("Invalid request")
        else:
            item = db[collection].find({"_id": ObjectId(source["_id"])})
            return dumps(item)

    except Exception:
        raise


# CREATE POST
# Insert an item and return its ID
@app.route('/create/<collection>', methods=['POST'])
def create(collection):
    try:
        if len(request.args) == 0 and len(request.form) == 0:
            raise Exception("Invalid request")
        else:
            source = request.args if len(request.args) > 0 else request.form
            _request = dumps(source)
            inserted_id = db[collection].insert_one(loads(_request)).inserted_id
            return str(inserted_id)

    except Exception:
        raise


# UPDATE PUT
# Expects an objectID parameter called "_id" and a "update_params" containing the desired changes to be made
# Returns the amount of modified items
# TODO: gotta work hard on this one as it still have some hardcoded stuff
@app.route('/update/<collection>', methods=['PUT', 'PATCH'])
def update(collection):
    try:
        if len(request.args) == 0 and len(request.form) == 0:
            raise Exception("Invalid request")
        else:
            source = request.args if len(request.args) > 0 else request.form
            modified_count = db[collection].\
                update_one({"_id": ObjectId(source["_id"])},
                           {"$set": loads(source["update_params"])}).modified_count
            return str(modified_count)

    except Exception:
        raise


# DELETE
# Delete the matched object
# Returns code 0 when successful
@app.route('/delete/<collection>', methods=['DELETE'])
def delete(collection):
    try:
        if len(request.args) == 0 and len(request.form) == 0:
            raise Exception("Invalid request")
        else:
            source = request.args if len(request.args) > 0 else request.form
            _request = dumps(source)
            db[collection].delete_one(loads(_request))
            return str(0)

    except Exception:
        raise


# Filtering invalid requests
@app.route('/read/')
@app.route('/create/', methods=['GET', 'POST'])
@app.route('/delete/', methods=['GET', 'POST'])
@app.route('/update/', methods=['GET', 'POST'])
@app.route('/create/<collection>', methods=['GET'])
@app.route('/update/<collection>', methods=['GET', 'POST'])
@app.route('/delete/<collection>', methods=['GET', 'POST'])
def invalid_request(collection=None):
    raise Exception("Invalid request")

if __name__ == '__main__':
    app.run(debug=True)
