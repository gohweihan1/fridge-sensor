from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
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

        return jsonify({
            "message": "Image received and classified!",
            "item": object_name
        }), 200

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": f"Invalid base64 image: {str(e)}"}), 400

def classify_image(image_data):
    """
    Accepts raw image data (bytes), encodes it in base64, and sends it to the LLaMA 3.2 Vision model on Replicate
    """

    # Convert image bytes to base64 and format as Data URI
    encoded_data = base64.b64encode(image_data).decode("utf-8")
    image_uri = f"data:image/jpeg;base64,{encoded_data}"  # Adjust MIME type as needed

    # Define the input payload with a simple prompt
    input_data = {
        "image": image_uri,
        "prompt": "What is the single most prominent object in this image? Give a response in this format: ##<one word answer>##"
    }

    # Run the model on Replicate
    output = replicate.run(
        "lucataco/ollama-llama3.2-vision-11b:d4e81fc1472556464f1ee5cea4de177b2fe95a6eaadb5f63335df1ba654597af",
        input=input_data
    )

    # Process and return the response
    return "".join(output).strip().lower().capitalize().rstrip(".")

def extract_answer(output_text):
    match = re.search(r"##(.*?)##", output_text)
    if match:
        return match.group(1).strip().lower()
    return "unknown"

# 🔥 Run Flask app
if __name__ == '__main__':
    app.run(debug=True, port=8000)
