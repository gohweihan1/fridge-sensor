from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from functions import getInventory, addItems, deleteItem, classify_image
import re
import base64
import replicate

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

cred = credentials.Certificate("key/fridge-app-d9238-firebase-adminsdk-fbsvc-61910d67bd.json")  # Your Firebase service account JSON
firebase_admin.initialize_app(cred)
db = firestore.client()
inventory_ref = db.collection("fridgeInventory")  # Firestore collection

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"message": "Server is up and running!"})

@app.route('/inventory', methods=['GET'])
def get_inventory():
    try:
        return getInventory(inventory_ref)
    except Exception as e:
        print(f"ERROR: {e}")
        print("Error retrieving items from database")

@app.route('/inventory', methods=['POST'])
def add_item():
    data = request.json

    if not data or not isinstance(data, list):
        return jsonify({"error": "Expected a JSON list of objects with 'name' keys"}), 400

    return addItems(inventory_ref, data)



@app.route('/inventory', methods=['DELETE'])
def remove_item():
    data = request.json
    item_name = data.get("name")

    return deleteItem(inventory_ref, item_name)


@app.route("/classify", methods=["POST"])
def classify():
    data = request.get_json()

    if not data or "image" not in data:
        return jsonify({"error": "No image received"}), 400

    base64_image = data["image"]
    add_or_remove = data["action"]

    try:
        # Remove the header "data:image/jpeg;base64," if present
        if "," in base64_image:
            base64_image = base64_image.split(",")[1]

        # Remove any characters not part of base64
        base64_image = re.sub(r'[^A-Za-z0-9+/=]', '', base64_image)

        # Ensure proper padding
        missing_padding = len(base64_image) % 4
        if missing_padding:
            base64_image += '=' * (4 - missing_padding)

        #print(f"Base 64 Image: {base64_image}")

        # Try decoding the base64 string
        image_data = base64.b64decode(base64_image)
        # # ✅ Save it to disk for verification
        # with open("received_image.jpg", "wb") as f:
        #     f.write(image_data)
        
        object_name = classify_image(image_data)

        print(object_name)

        #database actions
        if (add_or_remove == "add"):
            data_to_add = [{ "name": object_name }]
            addItems(inventory_ref, data_to_add)
        elif (add_or_remove == "remove"):
            deleteItem(inventory_ref, object_name)

            return jsonify({
                "message": "Image classified and deleted from fridge inventory!",
                "item": object_name
            }), 200

        return jsonify({
            "message": "Image classified and added to fridge inventory!",
            "item": object_name
        }), 200

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": f"Invalid base64 image: {str(e)}"}), 400

# 🔥 Run Flask app
if __name__ == '__main__':
    app.run(debug=True, port=8000)
