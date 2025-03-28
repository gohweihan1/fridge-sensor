from typing import Dict, List, Any
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from huggingface_hub import InferenceClient
import textwrap

def get_recipe_recommendations(fridge_items: Dict[str, str], preferences: Dict[str, str],
                                faiss_path: str, recipe_metadata_path: str) -> Dict:
    available_ingredients = [item.split(':')[0].strip() if ':' in item else item.strip()
                             for item, _ in fridge_items.items()]
    recipe_metadata = pd.read_csv(recipe_metadata_path)
    index = faiss.read_index(faiss_path)

    ingredient_text = ", ".join(fridge_items.keys())
    rag_text = (
        f"Recipe with {ingredient_text}. "
        f"Preferences: mealtype: {preferences.get('mealtype', '')}, "
        f"dietaryneeds: {preferences.get('dietaryneeds', '')}, "
        f"cuisinetype: {preferences.get('cuisinetype', '')}."
    )

    model = SentenceTransformer("all-MiniLM-L6-v2")
    if torch.cuda.is_available():
        model = model.to(torch.device("cuda"))
    search_embedding = model.encode([rag_text])[0].astype(np.float32)
    distances, indices = index.search(np.array([search_embedding]), 5)
    matching_recipes = recipe_metadata.iloc[indices[0]].to_dict('records')

    best_match = None
    best_score = -1
    missing_ingredients = []
    recipe_ingredients = []

    for i, recipe in enumerate(matching_recipes):
        curr_recipe_ingredients = []
        if 'ingredients' in recipe and recipe['ingredients']:
            if isinstance(recipe['ingredients'], str):
                curr_recipe_ingredients = [ing.strip() for ing in recipe['ingredients'].split(',')]
        elif 'ingredients_raw_str' in recipe and recipe['ingredients_raw_str']:
            curr_recipe_ingredients = [ing.strip() for ing in recipe['ingredients_raw_str'].split(',')]

        common = [i for i in curr_recipe_ingredients if i in available_ingredients]
        missing = [i for i in curr_recipe_ingredients if i not in available_ingredients]
        ingredient_score = len(common) / len(curr_recipe_ingredients) if curr_recipe_ingredients else 0

        preference_score = 0
        tags = recipe.get('tags', '').lower()
        if preferences.get('mealType', '').lower() in tags:
            preference_score += 1
        if isinstance(preferences.get('dietaryNeeds'), list):
            for need in preferences['dietaryNeeds']:
                if need.lower() in tags:
                    preference_score += 1
        elif isinstance(preferences.get('dietaryneeds'), str):
            if preferences['dietaryNeeds'].lower() in tags:
                preference_score += 1
        if preferences.get('cuisineType', '').lower() in tags:
            preference_score += 1

        num_prefs = 1 + (len(preferences['dietaryNeeds']) if isinstance(preferences['dietaryNeeds'], list) else 1) + 1
        preference_score = preference_score / num_prefs
        faiss_score = 1 - (distances[0][i] / max(distances[0]) if max(distances[0]) > 0 else 0)

        overall_score = (ingredient_score * 0.5) + (preference_score * 0.3) + (faiss_score * 0.2)

        if overall_score > best_score:
            best_score = overall_score
            best_match = recipe
            missing_ingredients = missing
            recipe_ingredients = curr_recipe_ingredients

    instructions = parse_instructions(best_match)
    instructions = [step.lstrip(" ,") for step in instructions]

    return {
        "recipe_name": best_match.get("name", "Unknown Recipe"),
        "customized_for": preferences,
        "ingredients_needed": recipe_ingredients,
        "instructions": instructions,
        "missing_ingredients": missing_ingredients,
        "match_score": best_score,
        "matching_recipes": matching_recipes
    }

#3
def build_prompt(context: str, fridge_items: Dict, preferences: Dict) -> str:
    # Format ingredients with quantities on separate lines for clarity
    ingredients_list = []
    for item, qty in fridge_items.items():
        if qty and str(qty).strip():
            ingredients_list.append(f"- {item}: {qty}")
        else:
            ingredients_list.append(f"- {item}")

    formatted_ingredients = "\n".join(ingredients_list)

    return (
        "You are a certified dietician and culinary expert.\n"
        "Your task is to create one personalized recipe using ONLY the ingredients available in the user's fridge.\n\n"

        "User Preferences:\n"
        f"- Meal Type: {preferences['mealType']}\n"
        f"- Dietary Needs: {', '.join(preferences['dietaryNeeds']) if isinstance(preferences['dietaryNeeds'], list) else preferences['dietaryNeeds']}\n"
        f"- Cuisine Type: {preferences['cuisineType']}\n\n"

        "AVAILABLE INGREDIENTS IN USER'S FRIDGE (all of these are available):\n"
        f"{formatted_ingredients}\n\n"

        "IMPORTANT INSTRUCTIONS:\n"
        "- You MUST use ONLY ingredients from the list above.\n"
        "- DO NOT mark any ingredient from the above list as 'Missing' - they are ALL available.\n"
        "- Do not invent or add any ingredients not listed above.\n"
        "- Only ingredients listed above may be used.\n"
        "- If a required ingredient is not listed (even honey, spices, etc.), you must clearly label it as 'Missing'.\n"
        "- Exception: water is allowed without marking it missing.\n"

        "- Match the preferences strictly (meal type, dietary needs, cuisine).\n"
        "- Provide clear, realistic ingredient quantities.\n\n"

        "Reference Recipe (for inspiration):\n"
        f"{context}\n\n"

        "Please generate exactly one recipe that includes:\n"
        "1. Recipe Name\n"
        "2. List of Ingredients with quantities\n"
        "3. Step-by-step Instructions\n"
        "4. Brief nutritional note explaining how this recipe meets the dietary needs"
    )

def parse_instructions(recipe):
    steps = recipe.get('steps', "")
    if isinstance(steps, list):
        return steps
    if isinstance(steps, str):
        import re, ast
        if steps.startswith("[") and steps.endswith("]"):
            try:
                return ast.literal_eval(steps)
            except:
                pass
        if '\n' in steps:
            return [step.strip() for step in steps.split('\n') if step.strip()]
        numbered_steps = re.findall(r'\d+\.\s*([^\d]+?)(?=\d+\.|$)', steps)
        if numbered_steps and len(numbered_steps) > 1:
            return [step.strip() for step in numbered_steps]
        return [s.strip() for s in re.split(r'(?<!\d)\.(?!\d)', steps) if s.strip()]
    return []

def get_final_recipe_response(recipe_dict, inventory_dict, preferences_dict):
    # Combine top-matching recipes into context
    matching_recipes = recipe_dict["matching_recipes"]

    recipe_context = "\n\n".join([
        f"{r['name']}: {r['ingredients']}. {r.get('steps', '')}" for r in matching_recipes
    ])

    # Create the prompt for the model
    prompt = build_prompt(recipe_context, inventory_dict, preferences_dict)

    # Generate recipe from LLM using the InferenceClient
    client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.1")
    response = client.text_generation(prompt, max_new_tokens=1000, temperature=0.1)

    print("Response received from LLM!")

    print(f"LLM Response: {response}")

    # Cleanly format the result
    result = {}

    if "Nutritional Note:" in response:
        # Split the response to separate the recipe and the nutritional note
        body, note = response.split("Nutritional Note:", 1)

        # Remove unwanted parts from the body (if necessary)
        body_cleaned = body.strip().replace("of the user.", "").strip()

        # Formatting the nutritional note
        result["recommended_recipe"] = body_cleaned
        result["nutritional_note"] = textwrap.fill(note.strip(), width=90)

    else:
        result["recommended_recipe"] = response.strip().replace("of the user.", "").strip()

    return result