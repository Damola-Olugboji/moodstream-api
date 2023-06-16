from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from firebase_admin import credentials, firestore
import firebase_admin
import json
import hashlib
# from Handler import Handler

import os

app = Flask(__name__)
CORS(app)

# create instance of firestore database

cred = credentials.Certificate(r"moodstream-e1c4f-firebase-adminsdk-1dlhj-220576a4d5.json")
# cred = credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
firebase_admin.initialize_app(cred)
db = firestore.client()

# endpoint for /luna/senators
@app.route('/assets/senators')
def get_senators():
    # read the senators data from the file
    with open('senators_data.json', 'r') as f:
        senators_data = json.load(f)

    # extract the senators dictionary from the data
    senators = senators_data['senators']

    # return the senators dictionary as a JSON response
    return jsonify(senators), 200, {'Content-Type': 'application/json', 'Charset': 'utf-8'}

@app.route('/assets/entities')
def get_entities():
    # read the senators data from the file
    with open('entities.json', 'r') as f:
        entities_data = json.load(f)

    # extract the senators dictionary from the data
    entities = entities_data['entities']

    # return the senators dictionary as a JSON response
    return jsonify(entities), 200, {'Content-Type': 'application/json', 'Charset': 'utf-8'}

# endpoint for sentiment/articles
#52d4dbce7c24d404d160413da8446790
@app.route('/sentiment/articles/<entity_id>', methods=['GET'])
def get_articles(entity_id):
    try:
        # get entity_id from query parameters

        # create a reference to the "articles" collection
        collection_ref = db.collection("Articles")

        # if entity_id is not specified, return all articles
        if entity_id is None:
            docs = collection_ref.stream()
        # if entity_id is specified, filter for articles with that entity_id
        else:
            docs = collection_ref.where('EntityID', '==', entity_id).stream()

        # store the articles in a list
        data = []

        # iterate through the returned documents
        for doc in docs:
            data.append(doc.to_dict())

        return jsonify({"data": data})

    except Exception as e:
        # return error message and status code
        return make_response(jsonify({"error": str(e)}), 500)
    
@app.route('/sentiment/trends/<entity_id>', methods=['GET'])
def get_trends(entity_id):
    try:
        # get entity_id from query parameters

        # create a reference to the keyword document
        keyword_ref = db.collection("Search Trends").document(entity_id)

        # create a reference to the "InterestOverTime" sub-collection
        collection_ref = keyword_ref.collection('InterestOverTime')

        # query the collection ordered by 'Time'
        docs = collection_ref.order_by('Time').stream()

        # store the data in a list
        data = []

        # iterate through the returned documents
        for doc in docs:
            # get the document data
            document_data = doc.to_dict()
            # append the document data to the list
            data.append(document_data)

        return jsonify({"data": data})

    except Exception as e:
        # return error message and status code
        return make_response(jsonify({"error": str(e)}), 500)

  
# endpoint for entities/
@app.route('/entities/<keyword>', methods=['GET'])
def get_entity_information(keyword):
    # retrieve query parameter from request object
    # keyword = request.args.get('query')
    query_hash = hashlib.md5(keyword.encode("utf-8")).hexdigest()
    
    doc_ref = db.collection("entities").document(query_hash)
    doc = doc_ref.get()
    doc = doc.to_dict()['data']
    
    # code to retrieve data from Firestore based on keyword and return as JSON
    return jsonify(doc)

if __name__ == '__main__':
    app.run(debug = True)
