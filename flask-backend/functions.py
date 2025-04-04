from flask import Flask, request, jsonify
import base64
import replicate
from recipe_generation import *
from typing import Dict, List, Any
import re

def getInventory(inventory_ref):
    items = inventory_ref.stream()
    
    # Create a list of dictionaries from the Firestore documents
    inventory_list = []
    for item in items:
        item_data = item.to_dict()
        item_data["name"] = item.id
        inventory_list.append(item_data)

    return inventory_list


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
        "prompt": "You are a fridge sensor designed to detect and identify common fridge items. \
        Please analyze the image and identify the single most prominent object in the frame. \
        The object should be a typical fridge inventory item such as fruits, vegetables, dairy products, or packaged foods. \
        Please respond in a singular, one-word format (e.g., 'apple', 'carrot', 'cheese'). \
        Your answer should only be the object name and nothing else. Respond in this format: <one word answer>"
    }

    # Run the model on Replicate
    output = replicate.run(
        "lucataco/ollama-llama3.2-vision-11b:d4e81fc1472556464f1ee5cea4de177b2fe95a6eaadb5f63335df1ba654597af",
        input=input_data
    )

    joined_output = "".join(output)
    print(joined_output)

    result = joined_output.strip().rstrip('.').capitalize()

    return result

def convert_inventory_list_to_dict(inventory_list: List[Dict[str, Any]]) -> Dict[str, str]:
    inventory_dict = {}

    for item_data in inventory_list:
        item_name = item_data.get("name")
        item_count = item_data.get("count")

        inventory_dict[item_name] = str(item_count)

    return inventory_dict

def generate_recipe(data, inventory_ref, FAISS_PATH ,RECIPE_METADATA_PATH):
    preferences_dict = data
    inventory_dict = convert_inventory_list_to_dict(getInventory(inventory_ref))

    recipe_dict = get_recipe_recommendations(inventory_dict, preferences_dict, FAISS_PATH, RECIPE_METADATA_PATH)

    print("Retrieved recipe recommendations!")

    response_dict = get_final_recipe_response(recipe_dict, inventory_dict, preferences_dict)

    print(response_dict)

    print("Got response, now to format.")

    return break_down_response_dict(response_dict)

def break_down_response_dict(recipe_data):
    # Extract the raw recipe string
    recommended_recipe = recipe_data.get('recommended_recipe', '')
    
    # Split the recipe string into parts
    parts = recommended_recipe.split("\n\n")  # Split by double newline, which separates the parts
    
    # Extract Recipe Name
    recipe_name = parts[0].replace("Recipe Name: ", "").strip() if len(parts) > 0 else ""
    
    # Extract Ingredients
    ingredients_section = parts[1].replace("List of Ingredients with quantities:", "").strip() if len(parts) > 1 else ""
    ingredients = [ingredient.strip().replace("-", "").strip() for ingredient in ingredients_section.split("\n") if ingredient.strip()]
    
    # Extract Instructions
    instructions_section = parts[3].strip() if len(parts) > 3 else ""
    instructions = [step.strip() for step in instructions_section.split("\n") if step.strip()]
    
    # Extract Nutritional Note (if available)
    nutritional_note = recipe_data.get('nutritional_note', '').strip()
    
    # Return the structured data as a dictionary
    return {
        "Nutritional_note": nutritional_note,
        "Recipe_name": recipe_name,
        "Ingredients": ingredients,
        "Step by step instructions": instructions
    }

