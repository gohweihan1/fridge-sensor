from flask import Flask, request, jsonify
import base64
import replicate

def getInventory(inventory_ref):
    items = inventory_ref.stream()
    
    # Create a list of dictionaries from the Firestore documents
    inventory_list = []
    for item in items:
        item_data = item.to_dict()
        item_data["name"] = item.id
        inventory_list.append(item_data)

    # Return the list as a JSON response
    return jsonify(inventory_list)


def addItems(inventory_ref, data):
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

def deleteItem(inventory_ref, item_name):
    item_name = item_name.lower().capitalize()
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