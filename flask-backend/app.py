from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("key/fridge-app-d9238-firebase-adminsdk-fbsvc-61910d67bd.json")  # Your Firebase service account JSON
firebase_admin.initialize_app(cred)
db = firestore.client()
inventory_ref = db.collection("fridgeInventory")  # Firestore collection

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"message": "Server is up and running!"})

@app.route('/inventory', methods=['GET'])
def get_inventory():
    items = inventory_ref.stream()
    
    # Create a list of dictionaries from the Firestore documents
    inventory_list = []
    for item in items:
        item_data = item.to_dict()
        item_data["name"] = item.id
        inventory_list.append(item_data)

    # Return the list as a JSON response
    return jsonify(inventory_list)

@app.route('/inventory', methods=['POST'])
def add_item():
    data = request.json

    if not data or not isinstance(data, list):
        return jsonify({"error": "Expected a JSON list of objects with 'name' keys"}), 400

    result = {}

    for item in data:
        item_name = item.get("name").lower().capitalize()

        if not item_name:
            return jsonify({"error": "Item name is required"}), 400

        doc_ref = inventory_ref.document(item_name)
        doc = doc_ref.get()

        if doc.exists:
            new_count = doc.to_dict().get("count", 0) + 1
            doc_ref.update({"count": new_count})
        else:
            new_count = 1
            doc_ref.set({"count": 1})

        result[item_name] = new_count

    return jsonify(result), 200



@app.route('/inventory', methods=['DELETE'])
def remove_item():
    data = request.json
    item_name = data.get("name")

    doc_ref = inventory_ref.document(item_name)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"error": "Item not found"}), 404

    count = doc.to_dict().get("count", 0)
    if count > 1:
        doc_ref.update({"count": count - 1})  # Decrement count
        return jsonify({"name": item_name, "count": count - 1})
    else:
        doc_ref.delete()  # Delete item if count reaches 0
        return jsonify({"message": f"{item_name} removed from inventory."})

# 🔥 Run Flask app
if __name__ == '__main__':
    app.run(debug=True, port=8000)
